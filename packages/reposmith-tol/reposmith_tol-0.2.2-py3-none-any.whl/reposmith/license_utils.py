from pathlib import Path
from datetime import datetime

from .core.fs import write_file

MIT = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def create_license(
    root_dir,
    license_type: str = "MIT",
    author: str = "Your Name",
    year: int | None = None,
    *,
    force: bool = False
) -> None:
    """
    Create a LICENSE file safely using the specified license type.

    Args:
        root_dir: The root directory where the LICENSE file will be created.
        license_type (str): The type of license to use. Currently only 'MIT' is supported.
        author (str): The author name to include in the license.
        year (int | None): The year to include in the license. Defaults to the current year.
        force (bool): If True, overwrite the LICENSE file if it exists.

    Raises:
        ValueError: If an unsupported license type is specified.

    Notes:
        - Does not overwrite existing LICENSE unless force=True.
        - Creates a .bak backup if the file is replaced.
        - Uses atomic write operation for file safety.
    """
    print("\n[10] Checking LICENSE")
    path = Path(root_dir) / "LICENSE"

    year = year or datetime.now().year
    if license_type.upper() == "MIT":
        content = MIT.format(year=year, author=author)
    else:
        raise ValueError(f"Unsupported license type: {license_type}")

    state = write_file(path, content, force=force, backup=True)

    if state == "exists":
        print("LICENSE already exists. Use --force to overwrite.")
    elif state == "written":
        print(f"LICENSE created/updated: {license_type} for {author} ({year})")
