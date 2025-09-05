import ffmpeg


class FFmpegRunner:
    def __init__(self, input_path, output_path, segment_duration, keyinfo_path, video_bitrate, scale):
        self.input_path = input_path
        self.output_path = output_path
        self.segment_duration = segment_duration
        self.keyinfo_path = keyinfo_path
        self.video_bitrate = video_bitrate
        self.scale = scale

    def run(self):
        (
            ffmpeg
            .input(self.input_path)
            .output(
                self.output_path,
                vf=f"scale={self.scale}",
                video_bitrate=self.video_bitrate,
                format='hls',
                hls_time=self.segment_duration,
                hls_list_size=0,
                hls_key_info_file=self.keyinfo_path,
            )
            .run()
        )