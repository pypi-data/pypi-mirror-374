
from dataclasses import dataclass
from typing import Optional
import uuid
import zipfile
from bs4 import BeautifulSoup

@dataclass
class Metadata:
    """代表EPUB書籍的中繼資料"""
    
    title: str
    language: str
    author: str
    identifier: Optional[str] = None
    
    def __post_init__(self):
        """後初始化處理"""
        if not self.identifier:
            self.identifier = str(uuid.uuid4())
    
    @classmethod
    def from_epub(cls, epub_file: zipfile.ZipFile) -> 'Metadata':
        """從現有的EPUB文件中提取中繼資料"""
        try:
            # 讀取content.opf文件
            opf_files = [name for name in epub_file.namelist() 
                        if name.endswith('.opf')]
            if not opf_files:
                raise ValueError("找不到OPF文件")
                
            with epub_file.open(opf_files[0]) as f:
                content = f.read().decode('utf-8')
                soup = BeautifulSoup(content, 'xml')
                
                # 提取必要的中繼資料
                metadata_tag = soup.find('metadata')
                if not metadata_tag:
                    raise ValueError("找不到中繼資料標籤")
                
                # 提取標題
                title = metadata_tag.find('dc:title')
                title = title.text if title else "未知標題"
                
                # 提取語言
                language = metadata_tag.find('dc:language')
                language = language.text if language else "zh"
                
                # 提取作者
                creator = metadata_tag.find('dc:creator')
                author = creator.text if creator else "未知作者"
                
                # 提取識別碼
                identifier = metadata_tag.find('dc:identifier')
                identifier = identifier.text if identifier else str(uuid.uuid4())
                
                return cls(
                    title=title,
                    language=language,
                    author=author,
                    identifier=identifier
                )
                
        except Exception as e:
            raise ValueError(f"從EPUB提取中繼資料時發生錯誤: {e}")

