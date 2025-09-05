
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup, Tag

from .chapter import Chapter
from .metadata import Metadata
from ..exceptions.epub_exceptions import EPUBError
from ..utils.logger import setup_logger

logger = setup_logger()


@dataclass
class Book:
    """Core class representing an EPUB book"""

    metadata: Metadata
    chapters: List[Chapter] = field(default_factory=list)
    _epub_book: Optional[epub.EpubBook] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize EPUB book object"""
        self._epub_book = epub.EpubBook()
        self._initialize_metadata()

    def _initialize_metadata(self):
        """Initialize book metadata"""
        self._epub_book.set_identifier(self.metadata.identifier)
        self._epub_book.set_title(self.metadata.title)
        self._epub_book.set_language(self.metadata.language)
        self._epub_book.add_author(self.metadata.author)

    def add_chapter(self, chapter: Chapter) -> None:
        """Add chapter to the book"""
        self.chapters.append(chapter)
        epub_chapter = chapter.to_epub_item()
        self._epub_book.add_item(epub_chapter)

    def add_cover(self, cover_path: str) -> None:
        """Add cover image to the book"""
        try:
            from pathlib import Path
            cover_file = Path(cover_path)
            if not cover_file.exists():
                logger.warning(f"Cover image not found: {cover_path}")
                return

            # Read cover image
            with cover_file.open('rb') as f:
                cover_content = f.read()

            # Create cover image item
            cover_image = epub.EpubItem(
                uid="cover",
                file_name="images/cover" + cover_file.suffix,
                media_type=f"image/{cover_file.suffix[1:]}",
                content=cover_content
            )

            # Add cover image to book
            self._epub_book.add_item(cover_image)

            # Create cover page
            cover_page = epub.EpubHtml(
                title="Cover",
                file_name="cover.xhtml",
                content=f"""
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <title>Cover</title>
                </head>
                <body>
                    <div style="text-align: center; page-break-after: always;">
                        <img src="images/cover{cover_file.suffix}" alt="Cover" style="max-width: 100%; height: auto;" />
                    </div>
                </body>
                </html>
                """
            )
            cover_page.id = "cover"
            cover_page.properties.append("cover")

            # Add cover page to book
            self._epub_book.add_item(cover_page)

            logger.info(f"Cover image added: {cover_path}")

        except Exception as e:
            logger.error(f"Error adding cover image: {e}")

    def get_spine(self) -> List[str]:
        """Get book's spine structure"""
        return ['nav'] + [ch.chapter_id for ch in self.chapters]

    def generate_epub(self, output_path: str) -> None:
        """Generate final EPUB file"""
        try:
            # Add TOC and navigation
            self._add_toc_and_nav()

            # Set spine
            self._epub_book.spine = self.get_spine()

            # Write EPUB file
            epub.write_epub(output_path, self._epub_book, {})
            logger.info(f"Successfully generated EPUB file: {output_path}")

        except Exception as e:
            raise EPUBError(f"Error generating EPUB file: {e}")

    def _add_toc_and_nav(self):
        """Add table of contents and navigation to EPUB"""
        from ..generators.toc import TOCGenerator
        toc_generator = TOCGenerator()
        nav_content = toc_generator.create_nav_content(self.chapters)

        nav = epub.EpubHtml(
            title='Table of Contents',
            file_name='nav.xhtml',
            content=nav_content
        )
        nav.id = 'nav'
        nav.properties.append('nav')

        self._epub_book.add_item(nav)

        # Set TOC structure correctly
        toc_sections = [epub.Section('Table of Contents', href='nav.xhtml')]
        for chapter in self.chapters:
            toc_sections.append(epub.Section(
                chapter.title, href=chapter.file_name))

        self._epub_book.toc = toc_sections
        self._epub_book.add_item(epub.EpubNcx())

    @classmethod
    def merge_existing_epub_with_new_chapters(cls,
                                              input_epub: str,
                                              new_text_file: str,
                                              output_file: str,
                                              convert_tags: bool = False) -> None:
        """合併新章節到現有的EPUB文件中"""
        try:
            from ..utils.file_handler import FileHandler
            file_handler = FileHandler()

            # 使用 ebooklib 直接讀取現有 EPUB
            existing_book = epub.read_epub(input_epub)

            # 從現有 EPUB 提取中繼資料
            title_meta = existing_book.get_metadata('DC', 'title')
            author_meta = existing_book.get_metadata('DC', 'creator')
            lang_meta = existing_book.get_metadata('DC', 'language')
            id_meta = existing_book.get_metadata('DC', 'identifier')

            metadata = Metadata(
                title=title_meta[0][0] if title_meta else 'Unknown Title',
                author=author_meta[0][0] if author_meta else 'Unknown Author',
                language=lang_meta[0][0] if lang_meta else 'zh',
                identifier=id_meta[0][0] if id_meta else 'unknown-id'
            )

            # 創建新的 Book 實例
            new_book = cls(metadata)
            new_book._epub_book = existing_book  # 使用現有的 EpubBook 物件

            # 處理新的文本內容
            new_content = file_handler.read_file(new_text_file)
            if new_content:
                from ..generators.content import ContentGenerator
                content_generator = ContentGenerator()
                # 計算現有章節數量
                existing_items = existing_book.get_items()
                existing_chapter_count = len([
                    item for item in existing_items
                    if isinstance(item, epub.EpubHtml) and
                    item.file_name.startswith('chapter_')
                ])
                new_chapters = content_generator.generate_chapters(
                    new_content,
                    convert_tags,
                    start_index=existing_chapter_count + 1
                )

                for chapter in new_chapters:
                    new_book.add_chapter(chapter)

            # 生成新的EPUB文件
            new_book.generate_epub(output_file)
            logger.info(f"成功合併章節並生成新的EPUB文件: {output_file}")

        except Exception as e:
            raise EPUBError(f"合併EPUB文件時發生錯誤: {e}")
