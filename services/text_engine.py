import re
import time

class LogicEngine:
    def __init__(self):
        # 1. CLEANING PATTERNS
        self.fillers = r"\b(um|uh|umm|ah|like|you know|basically|actually|literally|sort of|i mean|matlab|uhh)\b"
        
        # 2. TONE MAPPINGS
        self.formal_map = {
            "wanna": "want to", "gonna": "going to", "gotta": "have to",
            "can't": "cannot", "nope": "no", "yep": "yes", "thanks": "thank you",
            "cool": "excellent", "idk": "I do not know"
        }

    def pre_process(self, text):
        """Phase 1: Clean noise before Grammar"""
        # Remove fillers
        t = re.sub(self.fillers, "", text, flags=re.IGNORECASE).strip()
        # Remove repetitions
        t = re.sub(r'\b(\w+)( \1\b)+', r'\1', t, flags=re.IGNORECASE)
        return t

    def format_checklist(self, text):
        """
        Logic: If 'checklist' or 'list' is detected, split items into an array
        and format as bullet points.
        """
        # Remove the trigger phrase
        clean_t = re.sub(r'\b(make a|create a|here is a)?\s*(check)?list( of)?\b', '', text, flags=re.IGNORECASE).strip()
        
        # 1. Split text into an array based on common delimiters
        # Delimiters: " and ", " next ", " comma ", " also "
        delimiters = r'\b(and|next|comma|also|plus)\b'
        items = re.split(delimiters, clean_t, flags=re.IGNORECASE)
        
        # 2. Filter out the delimiters themselves from the array
        # (re.split keeps delimiters if capturing groups are used, so we filter)
        filtered_items = [item.strip() for item in items if item.strip() and not re.match(delimiters, item, re.IGNORECASE)]
        
        # 3. Construct Bullet List
        if len(filtered_items) > 0:
            formatted_list = "\nHere is the checklist:"
            for item in filtered_items:
                # Capitalize first letter of item
                item = item[0].upper() + item[1:] if item else item
                formatted_list += f"\n• {item}"
            return formatted_list
        
        return text

    def format_email(self, text):
        """
        Logic: Strict Email Structure
        """
        t = text
        
        # 1. Subject
        t = re.sub(r'\b(subject)\b[.,:]?\s*(.*)', r'\n\nSubject: \2', t, flags=re.IGNORECASE)
        
        # 2. Salutation (Dear Name,)
        # Captures: "Hi John", "Dear Manager"
        t = re.sub(r'\b(hi|hello|dear|good morning|good afternoon) (\w+)', r'\n\n\1 \2,\n', t, flags=re.IGNORECASE)
        
        # 3. Sign-off with Name (Regards Name)
        # Captures: "Regards John", "Thanks Team"
        # Logic: Newline -> Regards, -> Newline -> Name
        t = re.sub(r'\b(best regards|kind regards|regards|sincerely|thanks) (\w+)', r'\n\n\1,\n\2', t, flags=re.IGNORECASE)
        
        # 4. Standalone Sign-off (just "Regards")
        t = re.sub(r'\b(best regards|kind regards|regards|sincerely|thanks)\b[.,]?$', r'\n\n\1,\n', t, flags=re.IGNORECASE)

        return t

    def post_process(self, text, tone):
        """Phase 3: Apply Formatting Logic"""
        start = time.time()
        t = text

        # A. Apply Tone
        if tone == "formal":
            words = t.split()
            new_words = []
            for w in words:
                clean_w = w.strip(".,?!")
                if clean_w.lower() in self.formal_map:
                    rep = self.formal_map[clean_w.lower()]
                    if w.endswith('.'): rep += '.'
                    elif w.endswith(','): rep += ','
                    new_words.append(rep)
                else:
                    new_words.append(w)
            t = " ".join(new_words)

        # B. Check Intent
        
        # 1. CHECKLIST MODE
        if re.search(r'\b(check)?list\b', t, re.IGNORECASE):
            t = self.format_checklist(t)
            
        # 2. EMAIL MODE
        elif re.search(r'\b(email|letter)\b', t, re.IGNORECASE):
            t = self.format_email(t)

        # 3. STANDARD FORMATTING (Fallback)
        else:
            # Bullet triggers
            t = re.sub(r'\b(bullet point|next point|point)\b[.,:;]?\s*', '\n• ', t, flags=re.IGNORECASE)
            # Number triggers
            t = re.sub(r'\b(number one|first one|firstly)\b[.,:;]?\s*', '\n1. ', t, flags=re.IGNORECASE)
            t = re.sub(r'\b(number two|second one|secondly)\b[.,:;]?\s*', '\n2. ', t, flags=re.IGNORECASE)
            # Explicit newlines
            t = re.sub(r'\b(next line|new line|paragraph)\b[.,]?', '\n', t, flags=re.IGNORECASE)

        # Cleanup
        t = re.sub(r'\s+', ' ', t).replace(' \n', '\n').replace('\n ', '\n').strip()
        
        latency = (time.time() - start) * 1000
        return t, latency