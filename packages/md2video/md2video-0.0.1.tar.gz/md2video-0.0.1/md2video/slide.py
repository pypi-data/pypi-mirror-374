from .utils import *
from .md2image import *
from ffmpeg import FFmpeg, Progress
from ffmpeg.errors import FFmpegError

class Slide:
    def __init__(self, md_text):
        self.md_text = md_text
        self.parent = None
        self.base_path = None
        self.comments = None
        self.video_clip_path = None
    def get_lang(self):
        return self.parent.lang
    def set_parent(self, slides):
        self.parent = slides
    def set_base_path(self, base_path):
        self.base_path = base_path
    def set_comments(self, comments):
        self.comments = comments
    def create_audio(self, output_path):
        print("[!] Generating audios...")
        text_to_speech(self.comments, output_path, lang=self.get_lang())
        assert os.path.exists(output_path)
    def get_image_path(self):
        image_path = self.base_path + '.png'
        if os.path.exists(image_path):
            return image_path
        self.parent._create_images()
        assert os.path.exists(image_path)
        return image_path
    def _get_workdir(self):
        return self.parent.workdir
    def get_audio_path(self):
        assert self.base_path is not None
        audio_path = self.base_path + '.wav'
        if not os.path.exists(audio_path):
            self.create_audio(audio_path)
        return audio_path

    def create_video(self, out_path):
        try:
            # Create a video from image and audio using ffmpeg-python
            ffmpeg = FFmpeg() \
                .input(str(self.get_image_path()),loop=1) \
                .input(str(self.get_audio_path())) \
                .output(str(out_path), acodec='aac', vcodec='libx264',
                        framerate='30', pix_fmt='yuv420p', shortest=None,
                        s='1920x1080')

            @ffmpeg.on("progress")
            def on_progress(progress: Progress):
                print(progress)
            
            ffmpeg.execute()
            assert os.path.exists(out_path)
        except FFmpegError as e:
            print(e.message)

    def get_video_path(self):
        if self.video_clip_path is not None:
            return self.video_clip_path
        self.video_clip_path = self.base_path + '.mkv'
        if not os.path.exists(self.video_clip_path):
            self.create_video(self.video_clip_path)
        return self.video_clip_path


class Slides:
    def __init__(self, slides = []):
        self.data = slides # type: list[Slide]
        for s in slides:
            s.set_parent(self)
        self.workdir = None
        self.slide_html_path = None
        self.lang = None

    def set_lang(self, lang):
        self.lang = lang

    def set_workdir(self, workdir):
        self.workdir = workdir
        for i, s in enumerate(self.data):
            s.set_base_path(os.path.join(workdir, str(i + 1)))

    def to_slide_md_text(self):
        slides = self.data
        if len(slides) == 0:
            return []
        blocks = []
        for slide in slides:
            blocks.append(slide.md_text)
            if slide.comments is not None:
                blocks += [f'''::: notes
{slide.comments}
:::''']
            blocks += ['------------------------------------------------------------------------']
        blocks = blocks[:-1]
        return '\n\n'.join(blocks)

    def get_slide_html_path(self):
        if self.slide_html_path is not None:
            return self.slide_html_path
        slide_html = md_to_revealjs_html(self.to_slide_md_text())
        self.slide_html_path = os.path.join(self.workdir, "reveal.html")
        with open(self.slide_html_path, 'w') as f:
            f.write(slide_html)
        return self.slide_html_path

    def _create_images(self):
        print("[!] Generating images from slides...")
        revealjs_html_to_slide_images(self.get_slide_html_path(), self.workdir)

    def create_video(self, out_path):
        '''
        Uses ffmpeg filter_complex to concatenate videos, handling different video parameters
        https://stackoverflow.com/a/11175851
        '''
        print("[!] Concat videos...")
        if not os.path.exists(out_path):
            videos = []
            for slide in self.data:
                videos.append(slide.get_video_path())
            
            # Build filter complex string
            n_videos = len(videos)
            filter_complex = []
            
            # Add input arguments and build filter parts
            for i in range(n_videos):
                filter_complex.append(f'[{i}:v] [{i}:a]')

            filter_str = ' '.join(filter_complex)
            filter_str += f' concat=n={n_videos}:v=1:a=1 [v] [a]'

            # try:
            # Configure ffmpeg
            ffmpeg = FFmpeg()
            for i in range(n_videos):
                ffmpeg.input(str(videos[i]))
            ffmpeg.output(
                str(out_path),
                filter_complex=filter_str,
                map=['[v]', '[a]'],
            )

            @ffmpeg.on("progress")
            def on_progress(progress: Progress):
                print(progress)
                
            print(' '.join(ffmpeg.arguments))
            ffmpeg.execute()
            assert os.path.exists(out_path)
            # except FFmpegError as e:
            #     print(ffmpeg._process.stderr)
            #     raise e
        return out_path

    # def create_video(self, out_path):
    #     '''
    #     https://github.com/kkroening/ffmpeg-python/issues/96#issuecomment-401530613
    #     '''
    #     print("[!] Concat videos...")
    #     if not os.path.exists(out_path):
    #         videos = []
    #         for slide in self.data:
    #             videos.append(slide.get_video_path())
    #         # 用ffmpeg合并所有的video
    #         ffmpeg = FFmpeg()
    #         ffmpeg.input(f'concat:{"|".join(videos)}').output(str(out_path), c='copy')

    #         @ffmpeg.on("progress")
    #         def on_progress(progress: Progress):
    #             print(progress)
    #         ffmpeg.execute()
    #         assert os.path.exists(out_path)
    #     return out_path
