import click
import pdf2image
import openai
import tqdm

import os

import constants
import validation
import utils

from __version__ import __version__


@click.command(
    help='Convert your PDF documents to Markdown notes with KaTeX support with the help of OpenAI.',
    context_settings={'max_content_width': 120},
)
@click.version_option(__version__, '--version')
@click.option(
    '--pdf',
    help='The filepath of the PDF that you wish to convert.',
    required=True,
    callback=validation.file_exists,
)
@click.option(
    '--output',
    help='The filepath of the final markdown file.',
    required=True,
)
@click.option(
    '--openai-key',
    help='The OpenAI key used to perform the prompt queries.',
    required=True,
    callback=validation.openai_api_key,
)
@click.option(
    '--skip',
    help='Number of pages to skip.',
    default=0,
)
def cli(pdf: str, output: str, openai_key: str, skip: int) -> None:
    # Convert the PDF to images names 1, 2, 3, .., n in a temporary folder
    utils.print_banner()

    print(f"[-] Make sure that '{constants.CACHE_FOLDER}' exists.")
    utils.create_folder(constants.CACHE_FOLDER)

    print(f"[-] Make sure that '{output}' is empty.")
    utils.delete_file(output)

    print(f"[-] Convert '{pdf}' to images per page & save them in '{constants.CACHE_FOLDER}'.")
    try:
        images = pdf2image.convert_from_path(pdf)
        imagepaths = []
        for i, img in enumerate(
            tqdm.tqdm(
                iterable=images[skip:],
                desc='Converting images',
                bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}',
            ),
            start=1,
        ):
            imagepath = os.path.join(constants.CACHE_FOLDER, f'{i}.jpg')
            img.save(imagepath, 'JPEG')
            imagepaths.append(imagepath)
    except Exception:
        print('[!] An exception was raised.')
        print('    - Make sure that you entered a valid PDF file.')

    print('[-] Ask OpenAI to convert them to MD with KaTeX & append them to output file.')
    openai_client = openai.OpenAI(api_key=openai_key)
    openai_responses = []
    for img in tqdm.tqdm(imagepaths, desc='Requesting OpenAI', bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
        img_base64 = utils.img_to_base64(img)
        response = openai_client.responses.create(
            model='gpt-5-nano',
            input=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'input_text',
                            'text': (
                                'Convert the provided image into Markdown text. Follow these rules:\n\n'
                                '1. **Mathematical content:**\n'
                                '   - Write all mathematical expressions strictly in **KaTeX** syntax.\n'
                                '   - Use `$...$` for inline math.\n'
                                '   - Use `$$...$$` for display (multi-line or centered) math.\n\n'
                                '2. **Non-mathematical content:**\n'
                                '   - Preserve it in standard Markdown formatting (headings, lists, bold, italics, links, etc.).\n'
                                '   - Do not enclose plain text in math delimiters.\n\n'
                                '3. **General:**\n'
                                '   - Maintain the original structure and layout as closely as possible.\n'
                                '   - Ensure proper spacing between text and math expressions.\n'
                                '   - Do not include any extra commentary—output only the converted Markdown.'
                                '   - Do not use quotes (`>`).'
                            ),
                        },
                        {'type': 'input_image', 'image_url': f'data:image/png;base64,{img_base64}'},
                    ],
                }
            ],
        )
        openai_responses.append(response)
        openai_output = response.output[1].content[0].text
        openai_output = openai_output + '\n\n'
        utils.append_to_file(output, openai_output)

    print(f"[-] Successfully converted '{pdf}' to '{output}'.")

    print(f'[-] The final cost was {utils.calculate_openai_costs(openai_responses)}$')

    print(f"[-] Clear the '{constants.CACHE_FOLDER}' folder.")
    utils.clear_folder(constants.CACHE_FOLDER)


if __name__ == '__main__':
    cli()
