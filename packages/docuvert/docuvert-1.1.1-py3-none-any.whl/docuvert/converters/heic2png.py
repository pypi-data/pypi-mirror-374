import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# from core.ast import ASTNode  # Placeholder for future AST integration

try:
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Pillow is required for HEIC conversion: {e}")


class Heic2PngConverter:
    """Convert HEIC/HEIF image to PNG (retains alpha if available)."""

    def parse_heic2ast(self, input_path: str):  # type: ignore[override]
        return None

    def ast2png(self, ast_root, output_path: str):  # type: ignore[override]
        pass

    def convert(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".png"):
            output_path += ".png"

        # Avoid importlib.util checks; rely on direct import attempts
        errors: list[str] = []

        # 1. pillow-heif
        try:
            import pillow_heif  # type: ignore
            pillow_heif.register_heif_opener()
            with Image.open(input_path) as im:
                im.save(output_path, "PNG", optimize=True)
            print(f"Converted via pillow-heif: {output_path}")
            return
        except ModuleNotFoundError as e:
            errors.append(f"pillow-heif not installed: {e}")
        except Exception as e:  # pragma: no cover
            errors.append(f"pillow-heif failed: {e}")

        # 2. pyheif
        try:
            import pyheif  # type: ignore
            heif_file = pyheif.read(input_path)
            im = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            im.save(output_path, "PNG", optimize=True)
            print(f"Converted via pyheif: {output_path}")
            return
        except ModuleNotFoundError as e:
            errors.append(f"pyheif not installed: {e}")
        except Exception as e:  # pragma: no cover
            errors.append(f"pyheif failed: {e}")

        # 3. macOS sips -> intermediate JPEG -> PNG (lossy, last resort)
        if sys.platform == "darwin":
            try:
                import shutil
                if shutil.which("sips"):
                    tmp_jpg = output_path + ".intermediate.jpg"
                    result = subprocess.run([
                        "sips", "-s", "format", "jpeg", input_path, "--out", tmp_jpg
                    ], capture_output=True, text=True)
                    if result.returncode == 0 and os.path.exists(tmp_jpg):
                        with Image.open(tmp_jpg) as im:
                            im.save(output_path, "PNG", optimize=True)
                        os.remove(tmp_jpg)
                        print(f"Converted via sips→Pillow: {output_path}")
                        return
                    errors.append(f"sips failed: {result.stderr.strip()}")
                else:
                    errors.append("sips not found")
            except Exception as e:  # pragma: no cover
                errors.append(f"sips invocation failed: {e}")

        # 4. ImageMagick
        try:
            import shutil
            if shutil.which("magick"):
                result = subprocess.run(["magick", input_path, output_path], capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(output_path):
                    print(f"Converted via ImageMagick: {output_path}")
                    return
                errors.append(f"ImageMagick failed: {result.stderr.strip()}")
            else:
                errors.append("ImageMagick 'magick' not found")
        except Exception as e:  # pragma: no cover
            errors.append(f"ImageMagick invocation failed: {e}")

        raise ImportError(
            "HEIC→PNG conversion failed. Tried pillow-heif, pyheif, sips (macOS), ImageMagick.\n" +
            "Errors: " + " | ".join(errors) +
            "\nInstall one of: pillow-heif (preferred) or pyheif, or add a system tool (sips/magick)."
        )
