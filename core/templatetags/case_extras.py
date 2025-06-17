from django import template
import re

register = template.Library()

def is_likely_already_formatted(name_part):
    """
    Checks if a name part seems to be already intentionally formatted
    (e.g., contains uppercase chars other than the first, or special chars).
    """
    if not name_part:
        return False
    # Check for internal capitals (e.g., McDonald) or if it's all caps (e.g. USA)
    if any(c.isupper() for c in name_part[1:]) or name_part.isupper():
        return True
    # Check for mixed case with numbers or underscores (e.g., Devi_2)
    if re.search(r'[A-Z].*[0-9_]|[0-9_].*[A-Z]', name_part):
        return True
    # Check if it contains a period (e.g., Mrs.)
    if '.' in name_part:
        return True
    return False

@register.filter(name='smart_title')
def smart_title(value):
    if not isinstance(value, str):
        return value

    # Handle names with underscores by replacing them with spaces first for splitting
    processed_value = value.replace('_', ' ')

    words = processed_value.split(' ')
    capitalized_words = []
    for word in words:
        if not word: # Handles multiple spaces
            continue
        # If the word is something like "Mrs." or seems intentionally cased, leave it
        if is_likely_already_formatted(word):
            capitalized_words.append(word)
        else:
            capitalized_words.append(word.capitalize())
    
    result = ' '.join(capitalized_words)
    # Restore underscores if they were originally part of a "word" (e.g. Devi_2 needs to be handled carefully)
    # This part is tricky. The previous replacement handles most cases.
    # If strict underscore preservation for mixed-case like "Devi_2" is needed,
    # the logic would be more complex, possibly splitting by space and then by underscore.
    # For now, the space replacement and then capitalize should handle "kishor bhai seth" well.
    # "Mrs. Sunita Devi_2" would become "Mrs. Sunita Devi 2" then "Mrs. Sunita Devi 2" (no change as "Devi" is already cap)
    # Let's refine based on actual "Devi_2" output if needed.
    # A simpler approach for now is that `is_likely_already_formatted` will catch "Devi_2" if it sees "_"
    # and prevent capitalization.

    # Let's refine the check for names like "Devi_2"
    # If the original value had an underscore and mixed case, preserve it.
    if "_" in value and any(c.isupper() for c in value):
        temp_parts = value.split('_')
        # if any part of the original underscore-split value seems formatted, return original.
        if any(is_likely_already_formatted(p) for p in temp_parts):
            return value


    # Re-check based on common patterns for names that shouldn't just be title-cased
    # e.g. "McDonald", "O'Leary" - capitalize handles ' correctly
    # The `is_likely_already_formatted` should catch "Mrs." and "Devi_2" (if Devi_2 has an uppercase)
    
    # For simple names like "kishor bhai seth", this will work:
    # "kishor bhai seth" -> "Kishor Bhai Seth"

    # For "Mrs. Sunita Devi_2":
    # is_likely_already_formatted("Mrs.") -> True
    # is_likely_already_formatted("Sunita") -> True (if S is upper)
    # is_likely_already_formatted("Devi_2") -> True (if D is upper, and _ is present)
    # So it should preserve it.

    # Final pass to ensure we don't mess up already good names.
    if is_likely_already_formatted(value.split(' ')[0]): # Check first "word"
        # A bit of a heuristic: if the first part is already formatted (e.g. "Mrs."),
        # trust the original more.
        # We might still want to capitalize subsequent simple words.
        # This is getting complex, let's simplify the filter to be more direct.
        pass # Fall through to the capitalized_words logic

    return ' '.join(capitalized_words)


@register.filter(name='smart_title_v2')
def smart_title_v2(value):
    if not value or not isinstance(value, str):
        return value

    # Preserve parts like "Mrs.", "Dr.", etc.
    # Preserve parts with internal caps like "McDonald"
    # Preserve parts with numbers and underscores like "Devi_2"
    
    def capitalize_word(word):
        if not word:
            return ""
        # Check for prefixes, all caps, internal caps, or mixed alphanumeric with underscore
        if word.endswith('.') and len(word) > 1 and word[:-1].isalpha(): # like Mrs.
            return word 
        if word.isupper() and len(word) > 1: # like AI
            return word
        if any(c.isupper() for c in word[1:]): # like McDonald
            return word
        if re.search(r'[A-Za-z][0-9_]|[0-9_][A-Za-z]', word): # like Devi_2
            return word
        return word.capitalize()

    # Split by space, but handle multiple spaces
    parts = re.split(r'(\s+)', value) # Keep spaces for rejoining
    processed_parts = [capitalize_word(p) if p.strip() else p for p in parts]
    return "".join(processed_parts)