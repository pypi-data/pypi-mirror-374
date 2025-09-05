# src/df_gallery/cli.py
from __future__ import annotations
import argparse, csv, json, os, sys, time, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List
from df_gallery.template import HTML_TEMPLATE





# ---------- helpers (Python) ----------

def _scan_directory(dir_path: Path, extract_metadata: bool = False) -> List[Dict[str, Any]]:
    """Scan directory for image files and return list of metadata dictionaries."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
    rows: List[Dict[str, Any]] = []
    
    for img_path in dir_path.rglob('*'):
        if img_path.is_file() and img_path.suffix.lower() in image_extensions:
            try:
                # Basic metadata
                stat = img_path.stat()
                relative_path = str(img_path.relative_to(dir_path))
                row = {
                    'filename': relative_path,
                    'src': relative_path,  # HTML template expects 'src' field
                    'extension': img_path.suffix.lower(),
                    'filesize_bytes': stat.st_size,
                    'modified_time': stat.st_mtime,
                }
                
                # Optional detailed metadata extraction
                if extract_metadata:
                    try:
                        from PIL import Image
                        with Image.open(img_path) as img:
                            row.update({
                                'width': img.width,
                                'height': img.height,
                                'format': img.format,
                                'mode': img.mode,
                                'has_alpha_channel': 'A' in img.mode or img.mode == 'RGBA',
                            })
                    except Exception:
                        # If PIL fails, continue without detailed metadata
                        pass
                
                rows.append(row)
            except Exception:
                # Skip files that can't be accessed
                continue
    
    return rows

def _coerce_value(v: str):
    s = (v or "").strip()
    if s == "":
        return None
    lo = s.lower()
    if lo in ("true", "false"):
        return lo == "true"
    if lo in ("none", "null", "nan"):
        return None
    try:
        return int(s)
    except Exception:
        pass
    try:
        return float(s)
    except Exception:
        pass
    return v

def _rel_to(base: Path, target: Path) -> str:
    try:
        return os.path.relpath(target.resolve(), base).replace("\\", "/")
    except Exception:
        return str(target).replace("\\", "/")

def _read_rows(csv_path: Path, path_col: str, img_root: str, out_dir: Path, relative_to_html: bool) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if path_col not in (reader.fieldnames or []):
            raise SystemExit(f"Column '{path_col}' not found. Available: {reader.fieldnames}")
        for r in reader:
            raw = (r.get(path_col) or "").strip()
            if not raw:
                continue
            row = {k: _coerce_value(v if v is not None else "") for k, v in r.items()}
            if raw.startswith(("http://", "https://", "data:")):
                src = raw
            else:
                p = Path(raw)
                if img_root:
                    p = Path(img_root) / p
                src = _rel_to(out_dir, p) if relative_to_html else str(p).replace("\\", "/")
            row["src"] = src
            rows.append(row)
    return rows

def _render_html(*, title: str, rows: List[Dict[str, Any]], chunk_size: int, tile_px: int,
                 show_cols: List[str] | None, collapse_meta: bool, page_size: int) -> str:
    return HTML_TEMPLATE.format(
        title=title,
        rows_json=json.dumps(rows, ensure_ascii=False),
        chunk_size=max(1, int(chunk_size)),
        tile_px=max(80, int(tile_px)),
        show_cols_json=json.dumps(show_cols or []),
        meta_class=("meta-hidden" if collapse_meta else ""),
        toggle_text=("Show meta" if collapse_meta else "Hide meta"),
        page_size=max(1, int(page_size)),
    )

class _NoCacheHandler(SimpleHTTPRequestHandler):
    html_name: str = "index.html"
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()
    def log_message(self, fmt, *args):
        sys.stderr.write("[http] " + fmt % args + "\n")
    def do_GET(self):
        if self.path in ("/", ""):
            self.path = "/" + self.html_name
        return super().do_GET()

def _serve_file(html_path: Path, host: str, port: int, open_browser: bool):
    root = html_path.parent.resolve()
    
    # Change to the directory containing the HTML file
    original_cwd = os.getcwd()
    os.chdir(root)
    
    try:
        class CustomHandler(_NoCacheHandler):
            html_name = html_path.name
        
        httpd = ThreadingHTTPServer((host, port), CustomHandler)
        url = f"http://{host}:{port}/{html_path.name}"
        print(f"Serving {html_path} at {url} (Ctrl+C to stop)")
        # only try to open if there looks to be a display (avoid headless SSH spam)
        if open_browser and os.environ.get("DISPLAY") and not os.environ.get("SSH_CONNECTION"):
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    finally:
        os.chdir(original_cwd)  # Restore original directory

# ---------- subcommands ----------

def cmd_build(args) -> int:
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def build_once() -> List[Dict[str, Any]]:
        rows = _read_rows(
            csv_path=Path(args.csv),
            path_col=args.path_col,
            img_root=args.img_root,
            out_dir=out_path.parent,
            relative_to_html=args.relative_to_html,
        )
        if not rows:
            raise SystemExit("No image paths found.")
        html = _render_html(
            title=args.title,
            rows=rows,
            chunk_size=args.chunk,
            tile_px=args.tile,
            show_cols=args.show_cols,
            collapse_meta=args.collapse_meta,
            page_size=args.page_size,
        )
        out_path.write_text(html, encoding="utf-8")
        print(f"Wrote {out_path} with {len(rows)} items. Columns: {list(rows[0].keys())}")
        return rows

    # initial build
    build_once()

    # serve/watch if requested
    if not (args.serve or args.watch):
        return 0

    if args.watch:
        last_mtime = Path(args.csv).stat().st_mtime
        import threading
        def watch_loop():
            nonlocal last_mtime
            print(f"Watching {args.csv} for changes…")
            while True:
                try:
                    m = Path(args.csv).stat().st_mtime
                    if m != last_mtime:
                        last_mtime = m
                        print("Change detected, rebuilding…")
                        try:
                            build_once()
                        except Exception as e:
                            print(f"Rebuild error: {e}", file=sys.stderr)
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
        t = threading.Thread(target=watch_loop, daemon=True)
        t.start()
        _serve_file(out_path, args.host, args.port, args.open_browser)
        return 0
    else:
        _serve_file(out_path, args.host, args.port, args.open_browser)
        return 0

def cmd_serve(args) -> int:
    html_path = Path(args.html).resolve()
    if not html_path.exists():
        print(f"error: file not found: {html_path}", file=sys.stderr)
        return 2
    _serve_file(html_path, args.host, args.port, args.open_browser)
    return 0

def cmd_serve_dir(args) -> int:
    """Serve images from a directory by generating HTML on-the-fly."""
    dir_path = Path(args.dir).resolve()
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"error: directory not found: {dir_path}", file=sys.stderr)
        return 2
    
    print(f"Scanning directory: {dir_path}")
    rows = _scan_directory(dir_path, extract_metadata=args.extract_metadata)
    
    if not rows:
        print("No image files found in directory", file=sys.stderr)
        return 1
    
    print(f"Found {len(rows)} images")
    
    # Generate HTML in memory
    html = _render_html(
        title=args.title,
        rows=rows,
        chunk_size=args.chunk,
        tile_px=args.tile,
        show_cols=args.show_cols,
        collapse_meta=args.collapse_meta,
        page_size=args.page_size,
    )
    
    # Write HTML file to the image directory so it can be served alongside images
    html_in_dir = dir_path / "gallery.html"
    print(f"Writing HTML file to: {html_in_dir}")
    html_in_dir.write_text(html, encoding="utf-8")
    print(f"HTML file created successfully: {html_in_dir.exists()}")
    
    # Use the existing _serve_file function which properly handles server setup
    _serve_file(html_in_dir, args.host, args.port, args.open_browser)
    
    return 0

def main() -> int:
    ap = argparse.ArgumentParser(prog="df-gallery", description="Build and serve filterable, paginated HTML image galleries.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # build subcommand
    b = sub.add_parser("build", help="Build gallery HTML from CSV (optionally serve/watch).")
    b.add_argument("csv", help="Path to CSV with an image path column (default 'filename').")
    b.add_argument("--out", "-o", default="gallery.html", help="Output HTML file")
    b.add_argument("--path-col", default="filename", help="CSV column containing image paths/URLs")
    b.add_argument("--img-root", default="", help="Optional prefix joined before each filename (e.g. /data/images)")
    b.add_argument("--relative-to-html", action="store_true", help="Make paths relative to the output HTML's folder")
    b.add_argument("--chunk", type=int, default=500, help="Tiles to add per render batch (default: 500)")
    b.add_argument("--tile", type=int, default=200, help="Base tile size in px (default: 200)")
    b.add_argument("--title", default="Image Gallery", help="HTML page title")
    b.add_argument("--show-cols", nargs="*", default=None, help="Subset of columns to show (defaults to all except 'src').")
    b.add_argument("--collapse-meta", action="store_true", help="Start with metadata hidden (global toggle controls all).")
    b.add_argument("--page-size", type=int, default=250, help="Initial page size (user can change in UI).")
    # serve/watch options for build
    b.add_argument("--serve", action="store_true", help="Start a local HTTP server after building")
    b.add_argument("--watch", action="store_true", help="Rebuild when the CSV changes (implies --serve)")
    b.add_argument("--host", default="127.0.0.1", help="Host for the server (default: 127.0.0.1)")
    b.add_argument("--port", type=int, default=8000, help="Port for the server (default: 8000)")
    b.add_argument("--open", dest="open_browser", action="store_true", help="Open browser after starting server")
    b.add_argument("--no-open", dest="open_browser", action="store_false", help="Do not open browser")
    b.set_defaults(open_browser=True, func=cmd_build)

    # serve subcommand
    s = sub.add_parser("serve", help="Serve an existing gallery HTML or serve images from a directory.")
    s.add_argument("html", nargs="?", help="Path to gallery.html (optional if --dir is used)")
    s.add_argument("--dir", help="Directory containing images to serve")
    s.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    s.add_argument("--port", type=int, default=8010, help="Port (default: 8010)")
    s.add_argument("--title", default="Image Gallery", help="Gallery title (for --dir mode)")
    s.add_argument("--extract-metadata", action="store_true", help="Extract detailed image metadata (requires PIL)")
    s.add_argument("--chunk", type=int, default=500, help="Tiles to add per render batch (default: 500)")
    s.add_argument("--tile", type=int, default=200, help="Base tile size in px (default: 200)")
    s.add_argument("--show-cols", nargs="*", default=None, help="Subset of columns to show (defaults to all except 'src').")
    s.add_argument("--collapse-meta", action="store_true", help="Start with metadata hidden (global toggle controls all).")
    s.add_argument("--page-size", type=int, default=250, help="Initial page size (user can change in UI).")
    s.add_argument("--open", dest="open_browser", action="store_true", help="Open browser after starting server")
    s.add_argument("--no-open", dest="open_browser", action="store_false", help="Do not open browser")
    s.set_defaults(open_browser=True, func=cmd_serve)

    args = ap.parse_args()
    
    # Handle serve command logic
    if args.cmd == "serve":
        if args.dir:
            # Directory mode - use cmd_serve_dir
            return cmd_serve_dir(args)
        elif args.html:
            # File mode - use cmd_serve
            return cmd_serve(args)
        else:
            print("error: must specify either HTML file or --dir", file=sys.stderr)
            return 2
    
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())