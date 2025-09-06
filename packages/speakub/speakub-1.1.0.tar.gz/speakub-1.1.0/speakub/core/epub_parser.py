#!/usr/bin/env python3
"""
Robust EPUB parser helpers: find OPF, parse manifest/spine, and robustly resolve
chapter hrefs inside the EPUB zip.

This implementation focuses on tolerant href resolution for many EPUB variations:
 - hrefs relative to OPF dir, absolute-like (leading slash), placed under OEBPS/OPS/content folders
 - missing extensions (try common extensions)
 - percent-encoding and unicode filenames (unquote)
 - case-insensitive basename fallback search
 - detailed logging on each step to help debugging when --debug + logfile enabled
 - structured TOC extraction following EPUB standards (nav.xhtml → toc.ncx → spine fallback)
"""

import logging
import os
import xml.etree.ElementTree as ET
import zipfile

from functools import lru_cache
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

logger = logging.getLogger(__name__)

# Try to import BeautifulSoup for HTML parsing, fallback if not available
try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning(
        "BeautifulSoup4 not available. Navigation document parsing will be limited."
    )


def normalize_src_for_matching(src: str) -> str:
    """
    Normalize a source path for reliable matching.
    - Decode URL percent-encoding (e.g., %20 -> ' ')
    - Remove path fragments and anchors (#)
    - Get the file's basename
    - Convert to lowercase
    """
    if not src:
        return ""
    try:
        # Remove anchor and decode
        path = unquote(src.split("#")[0])
        # Get basename and convert to lowercase
        basename = os.path.basename(path).lower()
        return basename
    except Exception:
        # If any error occurs, fallback to a simple lowercase version
        return src.lower()


class EPUBParser:
    def __init__(self, epub_path: str, trace: bool = False):
        self.epub_path = epub_path
        self.trace = bool(trace)
        self.zf: Optional[zipfile.ZipFile] = None
        self.opf_path: Optional[str] = None
        self.opf_dir: str = ""
        self.zip_namelist: List[str] = []

        # Performance optimizations with LRU cache
        self._opf_cache: Optional[Dict] = None  # Cache for OPF parsing results
        self._toc_cache: Optional[Dict] = None  # Cache for TOC data

    def open(self) -> None:
        """Open the epub (zip) and locate OPF (container.xml -> rootfile)."""
        try:
            self.zf = zipfile.ZipFile(self.epub_path, "r")
            self.zip_namelist = self.zf.namelist()
            # Locate container.xml
            try:
                container_bytes = self.zf.read("META-INF/container.xml")
            except KeyError:
                # Try case-insensitive search for META-INF/container.xml
                found = None
                for name in self.zip_namelist:
                    if name.lower().endswith("meta-inf/container.xml"):
                        found = name
                        break
                if found:
                    container_bytes = self.zf.read(found)
                else:
                    raise
            # parse container.xml
            try:
                root = ET.fromstring(container_bytes)
                # find rootfile element
                ns = {"cn": "urn:oasis:names:tc:opendocument:xmlns:container"}
                rf = root.find(".//cn:rootfile", ns)
                if rf is None:
                    # try without namespace
                    rf = root.find(".//rootfile")
                if rf is None:
                    raise RuntimeError("No rootfile found in container.xml")
                full_path = rf.attrib.get("full-path")
                if not full_path:
                    raise RuntimeError("rootfile missing full-path attribute")
                self.opf_path = full_path.replace("\\", "/")
                self.opf_dir = os.path.dirname(self.opf_path)
                if self.trace:
                    logger.debug(
                        "Found OPF at '%s', opf_dir='%s'", self.opf_path, self.opf_dir
                    )
            except Exception:
                logger.exception("Failed to parse container.xml to find OPF")
                raise
        except Exception:
            logger.exception("Failed to open EPUB zip")
            raise

    def close(self) -> None:
        try:
            if self.zf:
                self.zf.close()
        except Exception:
            logger.exception("Failed to close EPUB zip")

    def __enter__(self) -> "EPUBParser":
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _normalize_zip_path(self, p: Optional[str]) -> str:
        """Normalize zip path for consistent handling."""
        if not p:
            return ""
        p = p.replace("\\", "/")
        if p.startswith("/"):
            p = p.lstrip("/")
        # collapse redundant segments
        p = os.path.normpath(p).replace("\\", "/")
        if p.startswith("./"):
            p = p[2:]
        return p

    def _possible_extensions(self, href: str) -> List[str]:
        base, ext = os.path.splitext(href)
        exts = [ext] if ext else []
        for e in [".xhtml", ".html", ".htm", ".xml"]:
            if e not in exts:
                exts.append(e)
        return exts

    def _generate_candidates_for_href(self, href: Optional[str]) -> List[str]:
        """
        Given an href from manifest/spine, produce prioritized candidate zip entry names.
        """
        if not href:
            return []
        href_raw = href.strip()
        # unquote percent-encoding
        href_unq = unquote(href_raw)
        candidates: List[str] = []

        # raw normalized
        candidates.append(self._normalize_zip_path(href_unq))
        # strip leading slash
        candidates.append(self._normalize_zip_path(href_unq.lstrip("/")))

        # relative to OPF dir
        if self.opf_dir:
            candidates.append(
                self._normalize_zip_path(os.path.join(self.opf_dir, href_unq))
            )
            candidates.append(
                self._normalize_zip_path(
                    os.path.join(self.opf_dir, href_unq.lstrip("/"))
                )
            )

        # common prefixes
        common_prefixes = ("OEBPS", "OPS", "Content", "content", "EPUB", "html")
        for prefix in common_prefixes:
            candidates.append(self._normalize_zip_path(os.path.join(prefix, href_unq)))
            candidates.append(
                self._normalize_zip_path(os.path.join(prefix, href_unq.lstrip("/")))
            )

        # try with/without extensions if missing
        base = href_unq
        base_no_ext, ext = os.path.splitext(base)
        if not ext:
            for e in [".xhtml", ".html", ".htm", ".xml"]:
                candidates.append(self._normalize_zip_path(base_no_ext + e))
                if self.opf_dir:
                    candidates.append(
                        self._normalize_zip_path(
                            os.path.join(self.opf_dir, base_no_ext + e)
                        )
                    )
                for prefix in common_prefixes:
                    candidates.append(
                        self._normalize_zip_path(os.path.join(prefix, base_no_ext + e))
                    )

        # basename only fallback
        basename = os.path.basename(href_unq)
        if basename:
            candidates.append(self._normalize_zip_path(basename))

        # dedupe preserving order
        seen = set()
        out = []
        for c in candidates:
            if not c:
                continue
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
        if self.trace:
            logger.debug("Candidates for href '%s': %s", href, out)
        return out

    def _find_in_zip_by_basename(self, basename: str) -> Optional[str]:
        if not basename:
            return None
        base_lower = basename.lower()
        # first try exact matches
        for name in self.zip_namelist:
            if name == basename:
                return name
        # then try endswith match (case-insensitive)
        for name in self.zip_namelist:
            if name.lower().endswith("/" + base_lower) or name.lower().endswith(
                base_lower
            ):
                return name
        return None

    @lru_cache(maxsize=50)
    def _read_chapter_from_zip(self, src: str, zip_path: str) -> str:
        """
        Cached helper method to read chapter content from zip file.
        Uses functools.lru_cache for automatic LRU caching.

        Args:
            src: Source href from manifest
            zip_path: Resolved zip file path

        Returns:
            Decoded text content
        """
        if not self.zf:
            raise RuntimeError("EPUB zip not opened")

        try:
            raw = self.zf.read(zip_path)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
            if self.trace:
                logger.debug("Loaded chapter '%s' from '%s'", src, zip_path)
            return text
        except Exception:
            logger.exception(
                "Failed to read zip entry '%s' for src '%s'", zip_path, src
            )
            raise

    def read_chapter(self, src: str) -> str:
        """
        Robust read: try multiple candidate zip paths derived from src.
        Returns decoded text content if found; raises FileNotFoundError otherwise.
        Optimized with functools.lru_cache for better performance.
        """
        if not self.zf:
            raise RuntimeError("EPUB zip not opened")

        candidates = self._generate_candidates_for_href(src)
        tried = []

        # Try primary candidates
        for cand in candidates:
            tried.append(cand)
            if cand in self.zip_namelist:
                try:
                    # Use cached method for actual file reading
                    return self._read_chapter_from_zip(src, cand)
                except Exception:
                    logger.exception(
                        "Failed to read zip entry '%s' for src '%s'", cand, src
                    )

        # fallback: basename search (case-insensitive)
        basename = os.path.basename(unquote(src or ""))
        if basename:
            found = self._find_in_zip_by_basename(basename)
            if found:
                tried.append(found)
                try:
                    return self._read_chapter_from_zip(src, found)
                except Exception:
                    logger.exception(
                        "Failed to read fallback zip entry '%s' for src '%s'",
                        found,
                        src,
                    )

        # last resort: case-insensitive suffix match using src
        src_lower = (src or "").lower()
        for name in self.zip_namelist:
            if name.lower().endswith(src_lower) or name.lower().endswith(
                os.path.basename(src_lower)
            ):
                tried.append(name)
                try:
                    return self._read_chapter_from_zip(src, name)
                except Exception:
                    logger.exception(
                        "Failed to read candidate zip entry '%s' for src '%s'",
                        name,
                        src,
                    )

        logger.error("Chapter file not found for src '%s'. Tried: %s", src, tried)
        raise FileNotFoundError(f"Chapter file not found: {src} (tried: {tried})")

    def parse_toc(self) -> Dict:
        """
        Parse comprehensive TOC with proper EPUB standard support.
        Returns dict: {'book_title': ..., 'nodes': [...], 'spine_order': [...], 'toc_source': ..., 'raw_chapters': [...]}
        """
        try:
            return self.extract_structured_toc()
        except Exception as e:
            logger.warning(f"Structured TOC extraction failed: {e}")
            # Fallback to basic spine parsing
            return self._spine_fallback_toc()

    def extract_structured_toc(self) -> Dict:
        """
        Extract structured TOC following EPUB standards.
        Priority: nav.xhtml (EPUB3) → toc.ncx (EPUB2) → spine fallback
        Uses the robust parsing logic from epub-tts.py
        """
        if not self.zf or not self.opf_path:
            raise RuntimeError("EPUB not properly opened")

        logger.debug("--- Starting TOC Build Process ---")

        # Parse OPF first to get manifest and spine
        try:
            opf_bytes = self.zf.read(self.opf_path)
            logger.debug(f"Found OPF file path: {self.opf_path}")
        except KeyError:
            # try case-insensitive match
            found = None
            for name in self.zip_namelist:
                if name.lower() == self.opf_path.lower():
                    found = name
                    break
            if found:
                opf_bytes = self.zf.read(found)
                self.opf_path = found
                self.opf_dir = os.path.dirname(found)
            else:
                raise FileNotFoundError(f"OPF file not found: {self.opf_path}")

        # Use BeautifulSoup for more robust parsing (like in epub-tts.py)
        if HAS_BS4:
            opf = BeautifulSoup(opf_bytes, "xml")
        else:
            root = ET.fromstring(opf_bytes)
            # Convert to a format similar to BeautifulSoup for compatibility
            opf = root

        # Extract book title with proper whitespace handling
        book_title = self._extract_book_title_robust(opf)

        # Build manifest (id -> href mapping) with basedir handling
        basedir = os.path.dirname(self.opf_path)
        basedir = f"{basedir}/" if basedir else ""

        manifest = {}
        ncx = navdoc = None

        if HAS_BS4:
            # BeautifulSoup approach (from epub-tts.py)
            manifest_elem = opf.find("manifest")
            if manifest_elem:
                for item in manifest_elem.find_all("item"):
                    attrs = dict(item.attrs)
                    href = f"{basedir}{attrs.get('href', '')}"
                    item_id = attrs.get("id")
                    media_type = attrs.get("media-type", "")
                    properties = attrs.get("properties", "")

                    if item_id:
                        manifest[item_id] = {
                            "href": href,
                            "media_type": media_type,
                            "properties": properties,
                        }

                    # Look for NCX and nav documents
                    if media_type == "application/x-dtbncx+xml":
                        ncx = href
                        logger.debug(f"Found NCX file reference: {ncx}")
                    elif properties == "nav":
                        navdoc = href
                        logger.debug(f"Found NAV document reference: {navdoc}")
        else:
            # ElementTree approach (fallback)
            manifest_elem = opf.find(
                ".//{http://www.idpf.org/2007/opf}manifest"
            ) or opf.find(".//manifest")
            if manifest_elem is not None:
                for item in manifest_elem.findall(
                    "{http://www.idpf.org/2007/opf}item"
                ) or manifest_elem.findall("item"):
                    item_id = item.attrib.get("id")
                    href = item.attrib.get("href")
                    media_type = item.attrib.get("media-type", "")
                    properties = item.attrib.get("properties", "")

                    if item_id and href:
                        full_href = f"{basedir}{href}"
                        manifest[item_id] = {
                            "href": full_href,
                            "media_type": media_type,
                            "properties": properties,
                        }

                        if media_type == "application/x-dtbncx+xml":
                            ncx = full_href
                        elif properties == "nav":
                            navdoc = full_href

        # Extract spine order
        spine_order = []
        if HAS_BS4:
            spine_elem = opf.find("spine")
            if spine_elem:
                spine_items = spine_elem.find_all("itemref")
                spine_order = [
                    manifest[i["idref"]]["href"]
                    for i in spine_items
                    if i.get("idref") in manifest
                ]
        else:
            spine = opf.find(".//{http://www.idpf.org/2007/opf}spine") or opf.find(
                ".//spine"
            )
            if spine is not None:
                for itemref in spine.findall(
                    "{http://www.idpf.org/2007/opf}itemref"
                ) or spine.findall("itemref"):
                    idref = itemref.attrib.get("idref")
                    if idref and idref in manifest:
                        spine_order.append(manifest[idref]["href"])

        logger.debug(f"Successfully parsed spine with {len(spine_order)} items.")

        # Extract TOC entries using the priority logic from epub-tts.py
        raw_chapters = []
        toc_source = "None"

        # 1. Try EPUB3 navigation document (nav.xhtml)
        if navdoc:
            raw_chapters = self._parse_nav_document_robust(navdoc)
            if raw_chapters:
                toc_source = "nav.xhtml"
                logger.debug(f"--- Parsing TOC from {toc_source} ---")

        # 2. Try EPUB2 NCX document (toc.ncx)
        if not raw_chapters and ncx:
            raw_chapters = self._parse_ncx_document_robust(ncx, basedir)
            if raw_chapters:
                toc_source = "toc.ncx"
                logger.debug(
                    f"--- nav.xhtml parsing failed or empty, trying {toc_source} ---"
                )

        # 3. Fallback to spine order with filenames
        if not raw_chapters and spine_order:
            toc_source = "spine"
            logger.debug(f"--- No TOC found, falling back to {toc_source} ---")
            for s in spine_order:
                title = os.path.basename(s)
                title = os.path.splitext(title)[0]  # Remove extension
                title = title.replace("_", " ").replace(
                    "-", " "
                )  # Replace underscores/hyphens
                title = " ".join(
                    word.capitalize() for word in title.split()
                )  # Capitalize words
                logger.debug(f"  item: Creating chapter from spine: '{title}' -> '{s}'")
                raw_chapters.append(
                    {
                        "type": "chapter",
                        "title": title,
                        "src": s,
                        "normalized_src": normalize_src_for_matching(s),
                    }
                )

        # Apply grouping logic from epub-tts.py
        nodes = []
        current_group = None
        logger.debug("--- Finalizing Node Structure (Grouping) ---")

        for chap in raw_chapters:
            title = chap["title"]
            if chap.get("type") == "group_header":
                logger.debug(f"Creating new group from 'group_header': '{title}'")
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }
                nodes.append(current_group)
            elif (
                chap.get("type") == "chapter"
                and title.startswith("【")
                and title.endswith("】")
            ):
                logger.debug(
                    f"Creating new group from fallback pattern '〈...〉': '{title}'"
                )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }
                nodes.append(current_group)
            else:
                node = {"type": "chapter", "title": title, "src": chap.get("src")}
                if current_group:
                    logger.debug(
                        f"  Adding chapter '{title}' to group '{current_group['title']}'"
                    )
                    current_group["children"].append(node)
                else:
                    logger.debug(f"Adding chapter '{title}' as a top-level node.")
                    nodes.append(node)

        logger.debug(f"--- TOC Build Process Finished. Final source: {toc_source} ---")

        return {
            "book_title": book_title,
            "nodes": nodes,
            "spine_order": spine_order,
            "toc_source": toc_source,
            "raw_chapters": raw_chapters,
        }

    def _extract_book_title_robust(self, opf: Any) -> str:
        """Extract book title from OPF metadata with proper whitespace handling"""
        if HAS_BS4:
            # BeautifulSoup approach
            book_title_tag = opf.find("dc:title")
            if book_title_tag and book_title_tag.text:
                title = book_title_tag.text.strip()
                if title:
                    logger.debug(f"Extracted book title: '{title}'")
                    return title
                else:
                    logger.debug("-> dc:title tag was found, but it is EMPTY.")
            else:
                logger.debug("-> dc:title tag not found, using default filename.")
        else:
            # ElementTree approach
            title_elem = (
                opf.find(".//{http://purl.org/dc/elements/1.1/}title")
                or opf.find(".//{http://purl.org/dc/elements/1.1/}Title")
                or opf.find(".//title")
            )

            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
                if title:
                    return title

        return os.path.basename(self.epub_path)

    def _parse_nav_document_robust(self, nav_href: str) -> List[Dict[str, str]]:
        """Parse EPUB3 navigation document using the robust logic from epub-tts.py"""
        if not HAS_BS4:
            logger.warning(
                "BeautifulSoup4 not found, cannot parse nav.xhtml. Skipping."
            )
            return []

        try:
            nav_content = self.read_chapter(nav_href)
            nav_basedir = os.path.dirname(nav_href)
            nav_soup = BeautifulSoup(nav_content, "xml")

            # Look for the TOC navigation
            nav_toc = nav_soup.find("nav", attrs={"epub:type": "toc"})
            if not nav_toc:
                return []

            raw_chapters = []
            list_items = nav_toc.find_all("li")
            logger.debug(f"Found {len(list_items)} <li> items in nav.xhtml")

            for i, item in enumerate(list_items):
                span_tag = item.find("span")
                a_tag = item.find("a")

                if span_tag:
                    title = " ".join(span_tag.text.strip().split())
                    logger.debug(f"  item {i}: Found group header (<span>): '{title}'")
                    raw_chapters.append({"type": "group_header", "title": title})
                elif a_tag and a_tag.get("href"):
                    href = a_tag.get("href")
                    # Resolve href relative to the nav document
                    full_path = os.path.normpath(os.path.join(nav_basedir, href)).split(
                        "#"
                    )[0]
                    title = " ".join(a_tag.text.strip().split())
                    logger.debug(
                        f"  item {i}: Found chapter (<a>): '{title}' -> '{full_path}'"
                    )
                    raw_chapters.append(
                        {
                            "type": "chapter",
                            "title": title,
                            "src": full_path,
                            "normalized_src": normalize_src_for_matching(full_path),
                        }
                    )

            return raw_chapters
        except Exception as e:
            if self.trace:
                logger.debug(f"Failed to parse nav document {nav_href}: {e}")
            return []

    def _parse_ncx_document_robust(
        self, ncx_href: str, basedir: str
    ) -> List[Dict[str, str]]:
        """Parse EPUB2 NCX document using the robust logic from epub-tts.py"""
        try:
            ncx_content = self.read_chapter(ncx_href)
            if HAS_BS4:
                ncx_soup = BeautifulSoup(ncx_content, "xml")
                nav_points = ncx_soup.find_all("navPoint")
            else:
                root = ET.fromstring(ncx_content)
                nav_points = root.findall(
                    ".//{http://www.daisy.org/z3986/2005/ncx/}navPoint"
                )

            logger.debug(f"Found {len(nav_points)} <navPoint> items in toc.ncx")
            raw_chapters = []

            for i, navPoint in enumerate(nav_points):
                if HAS_BS4:
                    content = navPoint.find("content")
                    navLabel = navPoint.find("navLabel")
                    if content and navLabel and content.get("src"):
                        full_path = os.path.normpath(
                            os.path.join(basedir, content["src"])
                        ).split("#")[0]
                        title = " ".join(navLabel.text.strip().split())
                        logger.debug(
                            f"  item {i}: Found chapter: '{title}' -> '{full_path}'"
                        )
                        raw_chapters.append(
                            {
                                "type": "chapter",
                                "title": title,
                                "src": full_path,
                                "normalized_src": normalize_src_for_matching(full_path),
                            }
                        )
                else:
                    nav_label = navPoint.find(
                        ".//{http://www.daisy.org/z3986/2005/ncx/}text"
                    )
                    if nav_label is None:
                        nav_label = navPoint.find(".//text")

                    title = (
                        nav_label.text.strip()
                        if nav_label is not None and nav_label.text
                        else ""
                    )

                    content = navPoint.find(
                        "{http://www.daisy.org/z3986/2005/ncx/}content"
                    )
                    if content is None:
                        content = navPoint.find(".//content")

                    href = content.attrib.get("src", "") if content is not None else ""

                    if title and href:
                        full_path = os.path.normpath(os.path.join(basedir, href)).split(
                            "#"
                        )[0]
                        raw_chapters.append(
                            {
                                "type": "chapter",
                                "title": title,
                                "src": full_path,
                                "normalized_src": normalize_src_for_matching(full_path),
                            }
                        )

            return raw_chapters
        except Exception as e:
            if self.trace:
                logger.debug(f"Failed to parse NCX document {ncx_href}: {e}")
            return []

    def _spine_fallback_toc(self) -> Dict:
        """Emergency fallback: use basic spine parsing"""
        try:
            # This calls the original basic parsing logic
            if not self.zf or not self.opf_path:
                raise RuntimeError("EPUB not properly opened")

            opf_bytes = self.zf.read(self.opf_path)
            root = ET.fromstring(opf_bytes)

            # Extract manifest
            manifest = {}
            for item in root.findall(".//*[@id][@href]"):
                item_id = item.attrib.get("id")
                href = item.attrib.get("href")
                if item_id and href:
                    manifest[item_id] = href

            # Extract spine order
            spine_hrefs = []
            spine = root.find(".//spine") or root.find(".//{*}spine")
            if spine is not None:
                for itemref in spine.findall("itemref") or spine.findall("{*}itemref"):
                    idref = itemref.attrib.get("idref")
                    if idref:
                        href = manifest.get(idref)
                        if href:
                            spine_hrefs.append(href)

            # Build basic nodes list
            nodes = []
            raw_chapters = []
            for idx, href in enumerate(spine_hrefs, 1):
                title = os.path.basename(href)
                title = os.path.splitext(title)[0]
                chapter_data = {
                    "type": "chapter",
                    "title": title,
                    "src": href,
                    "index": idx,
                    "normalized_src": normalize_src_for_matching(href),
                }
                nodes.append(chapter_data)
                raw_chapters.append(chapter_data)

            book_title = self._extract_book_title_robust(root)

            return {
                "book_title": book_title,
                "nodes": nodes,
                "spine_order": spine_hrefs,
                "toc_source": "fallback",
                "raw_chapters": raw_chapters,
            }
        except Exception as e:
            logger.error(f"Even fallback TOC parsing failed: {e}")
            return {
                "book_title": os.path.basename(self.epub_path),
                "nodes": [],
                "spine_order": [],
                "toc_source": "error",
                "raw_chapters": [],
            }
