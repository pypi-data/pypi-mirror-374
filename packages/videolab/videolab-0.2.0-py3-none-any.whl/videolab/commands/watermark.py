import os
import av
from PIL import Image, ImageDraw, ImageFont


def _create_watermark_image(text, frame_width, frame_height):
    """Creates a transparent watermark image with text."""
    font_size = int(frame_height * 0.05)
    font = ImageFont.load_default(size=font_size)

    # use a dummy image to calculate text size
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top

    # create the watermark image
    img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-left, -top), text, font=font, fill=(255, 255, 255, 128))

    # calculate position
    x = frame_width - text_width - 20
    y = 20
    position = (x, y)

    return img, position


def _add_watermark(frame, watermark_img, position):
    """Overlays a watermark image onto a video frame."""
    img = frame.to_image()
    img.paste(watermark_img, position, watermark_img)

    new_frame = av.VideoFrame.from_image(img)
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    return new_frame


def watermark_command(args):
    """Adds a text watermark to a video."""
    output_file = args.output_file
    if output_file is None:
        base, ext = os.path.splitext(args.input_file)
        output_file = f"{base}_watermarked{ext}"

    with av.open(args.input_file, mode="r") as in_container:
        in_video_stream = next((s for s in in_container.streams if s.type == 'video'), None)
        if not in_video_stream:
            print("No video stream found.")
            return

        watermark_img, position = _create_watermark_image(
            args.text, in_video_stream.width, in_video_stream.height
        )

        with av.open(output_file, mode="w") as out_container:
            out_video_stream = out_container.add_stream_from_template(in_video_stream)

            for packet in in_container.demux(in_video_stream):
                for frame in packet.decode():
                    new_frame = _add_watermark(frame, watermark_img, position)
                    for new_packet in out_video_stream.encode(new_frame):
                        out_container.mux(new_packet)

            # flush the encoder
            for new_packet in out_video_stream.encode():
                out_container.mux(new_packet)


def register_subcommand(subparsers):
    """Register the 'watermark' subcommand."""
    parser = subparsers.add_parser(
        "watermark",
        help="Add a watermark to a video.",
        description="Adds a watermark to a video file."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input video file"
    )
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Path to save the watermarked video file, "
            "defaults: '<input_file>_watermarked.<ext>'"
        )
    )
    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help="The text for the watermark"
    )
    parser.set_defaults(func=watermark_command)
