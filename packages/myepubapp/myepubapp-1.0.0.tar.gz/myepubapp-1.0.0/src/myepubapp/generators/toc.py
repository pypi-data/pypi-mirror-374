
from typing import List
from ..core.chapter import Chapter
from ..exceptions.epub_exceptions import TOCError


class TOCGenerator:
    """Tool class for generating EPUB table of contents"""

    @staticmethod
    def create_nav_content(chapters: List[Chapter]) -> str:
        """Generate navigation content with proper nesting"""
        try:
            if not chapters:
                # Return minimal TOC for empty chapters
                return '''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh" xml:lang="zh">
<head><title>Table of Contents</title></head>
<body>
<nav epub:type="toc" id="toc">
<h1>Table of Contents</h1>
<ol></ol>
</nav>
</body>
</html>'''

            nav_content = [
                '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh" xml:lang="zh">',
                '<head><title>Table of Contents</title></head>',
                '<body>',
                '<nav epub:type="toc" id="toc">',
                '<h1>Table of Contents</h1>',
                '<ol>'
            ]

            # Build the TOC structure recursively
            def build_toc_level(chapter_list: List[Chapter], start_idx: int, target_level: int) -> int:
                """Recursively build TOC for a specific level"""
                i = start_idx
                while i < len(chapter_list):
                    chapter = chapter_list[i]
                    current_level = {'h1': 1, 'h2': 2,
                                     'h3': 3, 'intro': 0}[chapter.level]

                    if current_level < target_level:
                        # We've gone up a level, stop processing this level
                        break
                    elif current_level == target_level:
                        # Add this chapter at current level
                        nav_content.append(
                            f'<li><a href="{chapter.file_name}">{chapter.title}</a>')

                        # Check if next chapter is a child (higher level)
                        next_level = {'h1': 1, 'h2': 2, 'h3': 3, 'intro': 0}[
                            chapter_list[i + 1].level] if i + 1 < len(chapter_list) else 0

                        if next_level > current_level:
                            # Has children, create nested list
                            nav_content.append('<ol>')
                            i = build_toc_level(
                                chapter_list, i + 1, current_level + 1)
                            nav_content.append('</ol>')

                        nav_content.append('</li>')
                        i += 1
                    else:
                        # Skip chapters at deeper levels (they're handled by recursion)
                        i += 1

                return i

            # Start building from level 1
            build_toc_level(chapters, 0, 1)

            nav_content.extend(['</ol>', '</nav>', '</body>', '</html>'])
            return '\n'.join(nav_content)

        except Exception as e:
            raise TOCError(f"Error generating table of contents: {e}")
