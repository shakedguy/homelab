from PIL import Image
import os
from pathlib import Path
from typing import Annotated

import typer


cli = typer.Typer(help="Image Format Converter CLI",
                  add_completion=True, no_args_is_help=True)


def convert_image(
    input_path: str,
    output_path: str,
    output_format: str,
):
    """
    Convert an image to a different format

    Args:
        input_path: Path to input image file
        output_path: Path to output image file
        output_format: Output format (JPEG or PNG)
    """
    try:
        p = Path(input_path).resolve()
        if not p.exists():
            typer.echo(f"Input file {input_path} does not exist")
            raise typer.Abort()
        img = Image.open(str(p))

        # Convert to RGB mode if necessary (for JPEG conversion)
        if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA'):
            img = img.convert('RGB')

        # Save the image in desired format
        img.save(output_path, output_format)
        print(f"Successfully converted {input_path} to {output_path}")

    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")


@cli.command(help="Convert Image to a different format")
def convert(
    image_path: Annotated[str, typer.Argument(help="The image path")],
    output_format: Annotated[str, typer.Option(
        "-o", "--out", help="Output Format")] = 'JPEG',
):
    """
    Convert image to a different format

    Args:
        image_path: Path to the image file
        output_format: Output format (JPEG or PNG)
    """

    output_path = image_path.replace(
        os.path.splitext(image_path)[1],
        f'.{output_format.lower()}', 1)
    convert_image(input_path=image_path, output_path=output_path,
                  output_format=output_format)


# def batch_convert(input_directory, output_format='JPEG'):
#     """
#     Convert all WebP images in a directory
#     Args:
#         input_directory: Directory containing WebP files
#         output_format: 'JPEG' or 'PNG' (default: 'JPEG')
#     """
#     for filename in os.listdir(input_directory):
#         if filename.lower().endswith('.webp'):
#             input_path = os.path.join(input_directory, filename)
#             convert_webp(input_path, output_format)
if __name__ == "__main__":
    cli()
