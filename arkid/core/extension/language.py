
from abc import abstractmethod
from ninja import Schema
from typing import List, Optional, Literal
from pydantic import Field
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.models import LanguageData

class LanguageExtension(Extension):
    
    TYPE = "language"
    
    @property
    def type(self):
        return LanguageExtension.TYPE

    def load(self):
        super().load()
    
    def load_language_data(self, data, language_type=_("简体中文")):
        
        self.language_type = language_type
        self.extension_data = data
        
        extension = self.model
        
        language_data,_ = LanguageData.active_objects.get_or_create(extension=extension)
        language_data.extension_data = self.extension_data
        language_data.name = self.language_type
        
        language_data.save()
        
        self.refresh_lang_maps()
        
         
    
    