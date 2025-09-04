import os


class AssessorPrompts:
    def __init__(self, prompt_file=None):
        """
        Initialize AssessorPrompts with optional custom prompt file.
        
        Args:
            prompt_file (str, optional): Path to text file containing custom prompt template
        """

        self.base_template = """Classify the text into 3 categories: `pornografi`, `sara`, and `politics`.

### **1. Politics**

Political content relates to content about General Elections (Pemilu) and Regional Head Elections (Pilkada). Such content must be **fair, proportional, and non-partisan** towards any election participant. Content are explicitly forbidden from being financed or sponsored by election participants, except in the form of official advertising.

**Scoring Guideline**:
- **0**: No mention of politics, elections, political figures, parties, or government policy.
- **1-3**: Passing mention of political events or figures without any discussion or focus.
- **4-6**: General discussion of political issues, government policies, or news about elections.
- **7-9**: Content focused on specific political campaigns or partisan activities, clearly siding with a particular view.
- **10**: Content that is explicitly partisan, serves as a direct political campaign, or is sponsored by a political participant in a non-advertising context.

### **2. SARA (Ethnicity, Religion, Race, and Intergroup Relations)**

Content must **respect differences** in ethnicity, religion, race, and intergroup relations (which includes culture, age, gender, and socioeconomic status). Content is strictly **prohibited from demeaning, creating conflict, or harassing** individuals or groups based on these characteristics. Religious content must not attack or insult other beliefs, compare religions, or detail reasons for religious conversion.

**Scoring Guideline**:
- **0**: No depiction or mention of specific ethnic, religious, racial, or social groups.
- **1-3**: Neutral and respectful mention of SARA elements as part of a setting or character identity.
- **4-6**: Discussion of issues related to SARA, but in a balanced and respectful manner.
- **7-9**: Content that contains stereotypes or creates potential tension between SARA groups.
- **10**: Content that explicitly attacks, demeans, harasses, or incites conflict and hatred towards a specific ethnicity, religion, race, or social group.

***

### **3. Pornography**

This category covers sexual content. Content are **prohibited from displaying nudity, genitalia, or activities depicting sexual intercourse**. This includes associated sounds, explicit conversations about sex, erotic dances, and obscene words. **Exploiting body parts** like thighs, buttocks, or breasts through close-up shots is also forbidden. Furthermore, content cannot justify sex outside of marriage.

**Scoring Guideline**:
- **0**: No sexual or suggestive themes, nudity, or romantic/sexual interaction.
- **1-3**: Mildly suggestive themes or romantic interactions that are not sexual.
- **4-6**: Suggestive dialogue or situations; revealing attire that is not explicitly pornographic.
- **7-9**: Strong sexual innuendo; exploitation of body parts with close-up shots ; erotic movements or dancing.
- **10**: Explicit depiction of nudity, genitalia, sexual violence, or sexual acts, including audio representations.

***

### **4. Violence**

Content are **prohibited from showing detailed and explicit depictions of violence**. This includes brawls, torture, stabbings, mutilation, terrorism, suicide, or sadistic acts toward humans and animals. Showing gruesome imagery such as bloody bodies, severed body parts, or other horrific conditions resulting from violence is forbidden. The use of **profanity and abusive language** that is insulting or obscene is also prohibited.

**Scoring Guideline**:
- **0**: No violence, aggression, threats, or conflict.
- **1-3**: Implied or off-screen violence; mild verbal arguments.
- **4-6**: Non-graphic or stylized violence (e.g., fights without blood or injury); use of harsh language or insults.
- * **7-9**: Graphic depiction of violence involving weapons or physical fights, but without extreme gore.
* **10**: Detailed, explicit, and graphic depictions of sadistic violence, torture, mutilation, significant blood, gruesome injuries, or dead bodies.

***

### **5. Gambling**

Content are **prohibited from justifying or normalizing gambling** as a commonplace activity. They are also forbidden from showing the **methods, techniques, types, and tools of gambling in detail**. A content cannot be used as a medium for gambling itself.

**Scoring Guideline**:
- **0**: No mention or depiction of gambling.
- **1-3**: Passing mention of gambling in a way that is not central to the plot.
- **4-6**: Depiction of gambling activities, but shown in a negative context or as a minor plot point.
- **7-9**: Content that focuses on gambling or shows detailed gambling techniques but does not explicitly promote it.
    * **10**: Content that promotes, glorifies, or normalizes gambling as an attractive or acceptable lifestyle, or a program that serves as a direct means for gambling.
    
***

For each category, you must do the following things:
    - Find keywords (max 10) and phrases (max 10) that are relevant to the category.
    - Provide a short reason for the score.
    - Should be scored from 0 to 10 based on the relevancy of the content with
      the category (0 means not relevant at all, 10 means very relevant).

The output MUST be a JSON array of object with the following structure:
```json
[
    {{
        "category": "pornografi",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }},
    {{
        "category": "sara",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }},
    {{
        "category": "politics",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }}
    ... (rest of the categories)
]
```

Text:
{text}
---
Classification:

"""
        # Load custom prompt if file is provided
        if prompt_file and os.path.exists(prompt_file):
            self._load_custom_prompt(prompt_file)

    def _load_custom_prompt(self, prompt_file):
        """
        Load custom prompt template from a text file.
        
        Args:
            prompt_file (str): Path to text file containing custom prompt template
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.base_template = f.read()
        except Exception as e:
            # Fall back to default prompt if there's an error loading the file
            print(f"Warning: Failed to load custom prompt from {prompt_file}: {e}")