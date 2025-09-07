# -*- coding: utf-8 -*-
"""
quangdon English Phonemes - Mỹ-only version
49 phonemes gốc → 45 phonemes cho Mỹ
Author: ML researcher
"""

import re
from phonemizer import phonemize
from phonemizer.backend import EspeakBackend

# --------------------------
# American-only phoneme set
# --------------------------
VOCAB = frozenset(
    'AIWYbdfhijklmnpstuvwzðŋɑɔəɛɜɡɪɹʃʊʌʒʤʧˈˌθᵊOæɾᵻ'
)

# --------------------------
# Mapping from espeak to quangdon (US)
# --------------------------
FROM_ESPEAKS = sorted({
    '\u0303':'',        # remove tilde
    'a^ɪ':'I',          # diphthong "eye"
    'a^ʊ':'W',          # diphthong "ow"
    'd^ʒ':'ʤ',          # consonant cluster "j/dg"
    'e':'A',            # diphthong "eh"
    'e^ɪ':'A',          
    'r':'ɹ',            # r sound
    't^ʃ':'ʧ',          # consonant cluster "ch"
    'x':'k',            # replace x
    'ç':'k',            
    'ɐ':'ə',            # schwa
    'ɔ^ɪ':'Y',          # diphthong "oy"
    'ə^l':'ᵊl',         # small schwa
    'ɚ':'əɹ',           
    'ɬ':'l',
    'ʔ':'t',            
    'ʔn':'tᵊn',
    'ʔˌn\u0329':'tᵊn',
    'ʲ':'',
    'ʲO':'jO',
    'ʲQ':'jQ'
}.items(), key=lambda kv: -len(kv[0]))

def from_espeak(ps: str, british: bool=False) -> str:
    """Convert espeak phonemes to quangdon phonemes (US only)"""
    for old, new in FROM_ESPEAKS:
        ps = ps.replace(old, new)
    ps = re.sub(r'(\S)\u0329', r'ᵊ\1', ps).replace(chr(809), '')
    
    # US-only replacements
    ps = ps.replace('o^ʊ', 'O')
    ps = ps.replace('ɜːɹ', 'ɜɹ')
    ps = ps.replace('ɜː', 'ɜɹ')
    ps = ps.replace('ɪə', 'iə')
    ps = ps.replace('ː', '')
    
    return ps.replace('^', '')

# --------------------------
# Convert back quangdon → espeak
# --------------------------
def to_espeak(ps: str) -> str:
    ps = ps.replace('ʤ', 'dʒ').replace('ʧ', 'tʃ')
    ps = ps.replace('A', 'eɪ').replace('I', 'aɪ').replace('Y', 'ɔɪ')
    ps = ps.replace('O', 'oʊ').replace('W', 'aʊ')
    ps = ps.replace('ᵊ', 'ə')
    return ps

# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    text = 'merchantship'
    espeak_backend = EspeakBackend(language='en-us', preserve_punctuation=True, with_stress=True, tie='^')
    espeak_ps = phonemize([text], backend=espeak_backend)[0].strip()
    print("ESPEAK:", espeak_ps)
    
    ps = from_espeak(espeak_ps)
    print("QUANGDON (US):", ps)
    
    back_to_espeak = to_espeak(ps)
    print("Back to ESPEAK:", back_to_espeak)
    
    # check all phonemes are in VOCAB
    assert all(p in VOCAB for p in ps), "Some phonemes are not in VOCAB"
