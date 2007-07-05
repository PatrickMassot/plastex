#!/usr/bin/env python

"""
C.11.3 Bibliography and Citation (p208)

"""

import plasTeX, codecs
from plasTeX.Base.LaTeX.Sectioning import chapter, section
from plasTeX import Command, Environment
from Lists import List

log = plasTeX.Logging.getLogger()

class bibliography(chapter):
    args = 'files:str'
    linkType = 'bibliography'

    def invoke(self, tex):
        res = chapter.invoke(self, tex)
        self.title = self.ownerDocument.createElement('bibname').expand(tex)
        self.loadBibliographyFile(tex)
        return res

    def loadBibliographyFile(self, tex):
        # Load bibtex file
        try:
            file = tex.kpsewhich(tex.jobname+'.bbl')
            tex.input(codecs.open(file, 'r', self.ownerDocument.config['files']['input-encoding']))
        except OSError, msg:
            log.warning(msg)

class bibliographystyle(Command):
    args = 'style'
    
class thebibliography(List):
    args = 'widelabel'
    linkType = 'bibliography'
  
    class bibitem(List.item):
        args = '[ label ] key:str'

        def invoke(self, tex):
            res = List.item.invoke(self, tex)
            a = self.attributes
            # Put the entry into the global bibliography
            doc = self.ownerDocument
            bibitems = doc.userdata.getPath('bibliography/bibitems', {})
            bibitems[a['key']] = self
            doc.userdata.setPath('bibliography/bibitems', bibitems)
            self.ref = str(len([x for x in bibitems.values() 
                                  if not x.attributes['label']]))
            key = a['key']
            label = a.get('label')
            citations = doc.userdata.getPath('bibliography/citations', {})
            if not citations.has_key(key):
                if label is None:
                    label = doc.createDocumentFragment()
                    label.extend(self.ref)
                citations[key] = label
            doc.userdata.setPath('bibliography/citations', citations)
            return res

        @property
        def id(self):
            return self.attributes['key']

        def cite(self):
            doc = self.ownerDocument
            res = doc.createDocumentFragment()
            citations = doc.userdata.getPath('bibliography/citations', {})
            res.extend(citations.get(self.attributes['key']))
            res.idref = self
            return res

        def citation(self):
            return self.cite()

    def digest(self, tokens):
        if self.macroMode == Command.MODE_END:
            return
        for tok in tokens:
            if not isinstance(tok, thebibliography.bibitem):
                continue
            tokens.push(tok)
            break
        return List.digest(self, tokens)

class cite(Command):
    args = '[ text ] keys:list:str'

    @property
    def bibitems(self):
        # Get all referenced items
        output = []
        doc = self.ownerDocument
        for x in self.attributes['keys']:
            item = doc.userdata.getPath('bibliography/bibitems', {}).get(x)
            if item is None:
                log.warning('Bibliography item "%s" has no entry', x)
            else:
                output.append(item)
        return output

    @property
    def postnote(self):
        a = self.attributes
        if a['text'] is not None:
            return a['text']
        return ''

    def citation(self):
        return self.bibitems
            
class nocite(Command):
    args = 'keys:str'

class bibcite(Command):
    args = 'key:str info'

    def invoke(self, tex):
        Command.invoke(self, tex)
        value = self.attributes['info'].firstChild
        doc = self.ownerDocument
        citations = doc.userdata.getPath('bibliography/citations', {})
        citations[self.attributes['key']] = value
        doc.userdata.setPath('bibliography/citations', citations)

class citation(Command):
    pass

class bibstyle(Command):
    pass

class bibdata(Command):
    pass
