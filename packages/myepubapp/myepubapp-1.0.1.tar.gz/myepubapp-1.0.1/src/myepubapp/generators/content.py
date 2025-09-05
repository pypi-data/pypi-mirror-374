

import re
from typing import List, Dict
from ..core.chapter import Chapter
from ..exceptions.epub_exceptions import ContentGenerationError


class ContentGenerator:
    """Handles content generation"""

    def generate_chapters(self, content: str, convert_tags: bool = False, start_index: int = 1) -> List[Chapter]:
        """Generate chapter list from text content"""
        try:
            if convert_tags:
                content = self._convert_tags(content)

            chapters_data = self._split_into_chapters(content)
            return [
                self._create_chapter(data, index)
                for index, data in enumerate(chapters_data, start=start_index)
            ]
        except Exception as e:
            raise ContentGenerationError(f"Error generating chapters: {e}")

    def _convert_tags(self, content: str) -> str:
        """Convert HTML tags to Chinese book title marks"""
        return re.sub(r'<(.*?)>', r'《\1》', content)

    def _split_into_chapters(self, content: str) -> List[Dict]:
        """Split content into chapters"""
        chapters = []
        chapter_splits = re.split(r'(※ⅰ|※ⅱ|※ⅲ|※☆)', content)

        i = 1
        while i < len(chapter_splits):
            level_symbol = chapter_splits[i].strip()
            chapter_content = chapter_splits[i + 1].strip()

            level_map = {
                '※ⅰ': 'h1',
                '※ⅱ': 'h2',
                '※ⅲ': 'h3',
                '※☆': 'intro'  # New intro symbol
            }

            if level_symbol in level_map:
                if level_symbol == '※☆':
                    # Intro page: entire content as introduction
                    chapters.append({
                        'title': 'Introduction',
                        'content': chapter_content.strip(),
                        'level': 'intro'
                    })
                else:
                    # Regular chapter: first line as title, rest as content
                    title, *content_parts = chapter_content.split('\n', 1)
                    body = content_parts[0] if content_parts else ''

                    chapters.append({
                        'title': title.strip(),
                        'content': body.strip(),
                        'level': level_map[level_symbol]
                    })

            i += 2

        return chapters

    def _create_chapter(self, chapter_data: Dict, index: int) -> Chapter:
        """Create individual chapter"""
        file_name = f"chapter_{index:03d}.xhtml"
        content = chapter_data['content'] or '<p>This chapter currently has no content.</p>'

        if not content.startswith('<p>'):
            content = ''.join(
                f'<p>{p.strip()}</p>' for p in content.split('\n') if p.strip())

        return Chapter(
            title=chapter_data['title'],
            content=content,
            level=chapter_data['level'],
            file_name=file_name,
            chapter_id=f"chapter_{index:03d}"
        )

