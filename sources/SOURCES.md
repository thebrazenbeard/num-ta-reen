# Source provenance and precedence

User-authorized source folder:

`OneDrive/Documents/Books/The Wreckforge Chronicles/Races, Species, and Other Fauna/Ech'ta'reen (Phase Shifters)/Num'ta'reen Language/`

Five `.docx` files were read through the signed-in OneDrive connector. These text exports retain the connector's readable text extraction and are preserved as references; they are **not** claimed to be layout-exact Word reproductions. No source documents were edited or moved.

| Export in this repo | Original OneDrive filename | SHA-256 of original DOCX | Role |
| --- | --- | --- | --- |
| `reference_grammar_v2_updated_lphoneme.txt` | `Nûm’ta’reen Reference Grammar v2.0_UPDATED_lphoneme.docx` | `B47A6F9AF68AC2CA643AA01E59FAAF9C8E738A03D679B95921CB47998E5AF441` | **Current grammar** |
| `dictionary_v2_updated_lphoneme.txt` | `Complete Nûm’ta’reen Dictionary V2_UPDATED_lphoneme.docx` | `30B1F35AF78713D03B51CFCA20A957EB917FFAFA0A0E344D3E859409B5078C4A` | **Current dictionary** |
| `language_core_v1.txt` | `Nûm’ta’reen Language Core.docx` | `FE14A36C030908A1587B62FE316F53271613FD87C8620095139E9A0D274D6E7F` | Historical core |
| `reference_grammar_v2_original.txt` | `Nûm’ta’reen Reference Grammar v2.0.docx` | `A7D9D08B97BD82792219110421672354020EFFF3C03EE1545E705519CE727218` | Historical comparison |
| `dictionary_v2_original.txt` | `Complete Nûm’ta’reen Dictionary V2.docx` | `6B9256A379CBDB4FC52F9EF0CF8BD2EE83D9020ED5A6EFCDB068C21CBA9DAF76` | Historical comparison |

When documents disagree, the later **`UPDATED_lphoneme` pair wins**. The `/l/` phoneme is valid per the amended grammar. The older v1/v2 text is retained for provenance, not mixed indiscriminately into the current rules.

### Data generation

- `data/lexicon.json`: parsed from the updated dictionary's marked entries; the source line and lexical fields are retained for auditing.
- `data/corpus.json`: extracted from the updated grammar's annotated utterances; source free translations are privileged over mechanical word replacements.

The dictionary contains **500 unique entries**; a dictionary gloss is not necessarily a complete, context-independent English synonym.

These are original fictional worldbuilding materials. No open-source license or redistribution permission for the broader manuscript is asserted by this repository.
