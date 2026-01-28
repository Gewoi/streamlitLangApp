#!/usr/bin/env python3
"""
Bärndütsch Lesson Editor
A GUI application for creating and editing language lesson YAML files.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from copy import deepcopy

# Try to import ruamel.yaml for better YAML handling, fall back to PyYAML
try:
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import LiteralScalarString
    USING_RUAMEL = True
except ImportError:
    import yaml
    USING_RUAMEL = False


# =============================================================================
# Data Models
# =============================================================================

STEP_TYPES = {
    'markdown': 'Markdown Text',
    'introduce_word': 'Introduce Word',
    'cloze': 'Fill in the Blank (Cloze)',
    'order': 'Word Order',
    'translate_type': 'Translate & Type',
    'listen_type': 'Listen & Type',
    'true_false': 'True/False',
    'match': 'Match Pairs',
}

SECTIONS = ['Basics', 'Greetings', 'Numbers', 'Food', 'Travel', 'Conversation', 'Advanced']


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    # Replace umlauts and special chars
    replacements = {
        'ä': 'a', 'à': 'a', 'â': 'a',
        'ö': 'o', 'ò': 'o', 'ô': 'o',
        'ü': 'u', 'ù': 'u', 'û': 'u',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'ß': 'ss', 'ç': 'c',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')[:30]


def make_audio_path(name: str) -> str:
    """Create full audio path from just the filename."""
    if not name:
        return ""
    name = name.replace('.wav', '').strip()
    return f"data/assets/audio/{name}.wav"


def make_image_path(name: str) -> str:
    """Create full image path from just the filename."""
    if not name:
        return ""
    name = name.replace('.jpg', '').replace('.png', '').strip()
    return f"data/assets/images/{name}.jpg"


def extract_audio_name(path: str) -> str:
    """Extract just the filename from an audio path."""
    if not path:
        return ""
    match = re.search(r'data/assets/audio/(.+)\.wav$', path)
    return match.group(1) if match else path


def extract_image_name(path: str) -> str:
    """Extract just the filename from an image path."""
    if not path:
        return ""
    match = re.search(r'data/assets/images/(.+)\.jpg$', path)
    return match.group(1) if match else path


def ensure_solution_emoji(text: str) -> str:
    """Ensure solution_display starts with ✅ emoji."""
    if not text or not text.strip():
        return text
    text = text.strip()
    if not text.startswith('✅'):
        text = '✅ ' + text
    return text


# =============================================================================
# YAML Export
# =============================================================================

def export_to_yaml(lesson: Dict) -> str:
    """Export lesson data to properly formatted YAML string."""
    lines = []
    
    # Header
    lines.append(f'id: {lesson.get("id", "")}')
    lines.append(f'title: "{lesson.get("title", "")}"')
    lines.append(f'description: "{lesson.get("description", "")}"')
    lines.append(f'estimated_minutes: {lesson.get("estimated_minutes", 10)}')
    lines.append(f'section: {lesson.get("section", "Basics")}')
    lines.append('')
    lines.append('steps:')
    
    for step in lesson.get('steps', []):
        step_type = step.get('type', 'markdown')
        lines.append(f'  - type: {step_type}')
        lines.append(f'    id: {step.get("id", "")}')
        
        if step_type == 'markdown':
            lines.append('    markdown: |')
            for line in step.get('markdown', '').split('\n'):
                lines.append(f'      {line}')
            if step.get('images'):
                lines.append('    images:')
                for img in step['images']:
                    lines.append(f'      - "{img}"')
                    
        elif step_type == 'introduce_word':
            lines.append(f'    word: "{step.get("word", "")}"')
            lines.append('    translation:')
            lines.append(f'      en: "{step.get("translation", {}).get("en", "")}"')
            lines.append(f'      de: "{step.get("translation", {}).get("de", "")}"')
            if step.get('images'):
                lines.append('    images:')
                for img in step['images']:
                    lines.append(f'      - "{img}"')
            if step.get('audio'):
                lines.append(f'    audio: "{step["audio"]}"')
                
        elif step_type == 'cloze':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            lines.append('    sentence:')
            lines.append(f'      question: "{step.get("sentence", {}).get("question", "")}"')
            lines.append(f'      helper: "{step.get("sentence", {}).get("helper", "")}"')
            target = step.get("sentence", {}).get("target", ["", ""])
            lines.append(f'      target: ["{target[0] if len(target) > 0 else ""}", "{target[1] if len(target) > 1 else ""}"]')
            if step.get('answers'):
                answers_str = ', '.join(f'"{a}"' for a in step['answers'])
                lines.append(f'    answers: [{answers_str}]')
            if step.get('solution_display'):
                solution = ensure_solution_emoji(step['solution_display'])
                lines.append('    solution_display: |')
                for line in solution.split('\n'):
                    lines.append(f'      {line}')
            if step.get('images'):
                lines.append('    images:')
                for img in step['images']:
                    lines.append(f'      - "{img}"')
            if step.get('audio'):
                lines.append(f'    audio: "{step["audio"]}"')
                    
        elif step_type == 'order':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            lines.append('    sentence:')
            lines.append(f'      question: "{step.get("sentence", {}).get("question", "")}"')
            lines.append(f'      helper: "{step.get("sentence", {}).get("helper", "")}"')
            if step.get('tokens'):
                tokens_str = ', '.join(f'"{t}"' for t in step['tokens'])
                lines.append(f'    tokens: [{tokens_str}]')
            if step.get('solution_display'):
                solution = ensure_solution_emoji(step['solution_display'])
                lines.append('    solution_display: |')
                for line in solution.split('\n'):
                    lines.append(f'      {line}')
            if step.get('audio'):
                lines.append(f'    audio: "{step["audio"]}"')
                    
        elif step_type == 'translate_type':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            lines.append('    sentence:')
            lines.append(f'      question: "{step.get("sentence", {}).get("question", "")}"')
            lines.append(f'      helper: "{step.get("sentence", {}).get("helper", "")}"')
            if step.get('answers'):
                lines.append('    answers:')
                answers_str = ', '.join(f'"{a}"' for a in step['answers'])
                lines.append(f'      [{answers_str}]')
            if step.get('images'):
                lines.append('    images:')
                for img in step['images']:
                    lines.append(f'      - "{img}"')
            if step.get('solution_display'):
                solution = ensure_solution_emoji(step['solution_display'])
                lines.append('    solution_display: |')
                for line in solution.split('\n'):
                    lines.append(f'      {line}')
                    
        elif step_type == 'listen_type':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            lines.append(f'    audio: "{step.get("audio", "")}"')
            if step.get('answers'):
                answers_str = ', '.join(f'"{a}"' for a in step['answers'])
                lines.append(f'    answers: [{answers_str}]')
            if step.get('images'):
                lines.append('    images:')
                for img in step['images']:
                    lines.append(f'      - "{img}"')
            if step.get('solution_display'):
                solution = ensure_solution_emoji(step['solution_display'])
                lines.append('    solution_display: |')
                for line in solution.split('\n'):
                    lines.append(f'      {line}')
                    
        elif step_type == 'true_false':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            if step.get('audio'):
                lines.append(f'    audio: "{step["audio"]}"')
            lines.append(f'    text: "{step.get("text", "")}"')
            lines.append(f'    answer: "{step.get("answer", "True")}"')
            if step.get('solution_display'):
                solution = ensure_solution_emoji(step['solution_display'])
                lines.append('    solution_display: |')
                for line in solution.split('\n'):
                    lines.append(f'      {line}')
                    
        elif step_type == 'match':
            lines.append(f'    prompt: "{step.get("prompt", "")}"')
            lines.append('    pairs:')
            for pair in step.get('pairs', []):
                lines.append(f'      - left: "{pair.get("left", "")}"')
                lines.append(f'        right: "{pair.get("right", "")}"')
        
        lines.append('')  # Empty line between steps
    
    return '\n'.join(lines)


def load_yaml(filepath: str) -> Dict:
    """Load a YAML file and return the lesson data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        if USING_RUAMEL:
            yaml_parser = YAML()
            return dict(yaml_parser.load(f))
        else:
            return yaml.safe_load(f)


# =============================================================================
# GUI Components
# =============================================================================

class ScrollableFrame(ttk.Frame):
    """A scrollable frame widget."""
    
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


class FilePathEntry(ttk.Frame):
    """Entry widget for file paths with automatic path building."""
    
    def __init__(self, parent, label: str, path_type: str = 'audio', **kwargs):
        super().__init__(parent, **kwargs)
        self.path_type = path_type
        
        ttk.Label(self, text=label, width=15, anchor='e').pack(side='left', padx=(0, 5))
        
        self.entry = ttk.Entry(self, width=30)
        self.entry.pack(side='left', fill='x', expand=True)
        
        ext = '.wav' if path_type == 'audio' else '.jpg'
        ttk.Label(self, text=ext, foreground='gray').pack(side='left', padx=(2, 0))
    
    def get(self) -> str:
        """Get the full path."""
        name = self.entry.get().strip()
        if not name:
            return ""
        if self.path_type == 'audio':
            return make_audio_path(name)
        return make_image_path(name)
    
    def set(self, path: str):
        """Set from a full path."""
        self.entry.delete(0, tk.END)
        if self.path_type == 'audio':
            self.entry.insert(0, extract_audio_name(path))
        else:
            self.entry.insert(0, extract_image_name(path))


class ImageListEditor(ttk.Frame):
    """Widget for editing a list of image paths."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text="Images:", width=15, anchor='e').pack(side='left')
        ttk.Button(header, text="+ Add", command=self.add_image, width=8).pack(side='right')
        
        # List frame
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill='x', pady=5)
        
        self.entries = []
    
    def add_image(self, value: str = ""):
        """Add a new image entry."""
        row = ttk.Frame(self.list_frame)
        row.pack(fill='x', pady=2)
        
        entry = ttk.Entry(row, width=30)
        entry.pack(side='left', fill='x', expand=True, padx=(95, 5))
        entry.insert(0, extract_image_name(value))
        
        ttk.Label(row, text='.jpg', foreground='gray').pack(side='left')
        
        def remove():
            self.entries.remove((row, entry))
            row.destroy()
        
        ttk.Button(row, text="×", width=2, command=remove).pack(side='left', padx=5)
        self.entries.append((row, entry))
    
    def get(self) -> List[str]:
        """Get all image paths."""
        return [make_image_path(e.get()) for _, e in self.entries if e.get().strip()]
    
    def set(self, images: List[str]):
        """Set images from a list of paths."""
        # Clear existing
        for row, _ in self.entries:
            row.destroy()
        self.entries = []
        
        # Add new
        for img in (images or []):
            self.add_image(img)


class AnswersEditor(ttk.Frame):
    """Widget for editing a list of acceptable answers."""
    
    def __init__(self, parent, label: str = "Answers:", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Header with add entry
        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text=label, width=15, anchor='e').pack(side='left')
        
        self.add_entry = ttk.Entry(header, width=25)
        self.add_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.add_entry.bind('<Return>', lambda e: self.add_answer())
        
        ttk.Button(header, text="+ Add", command=self.add_answer, width=8).pack(side='left')
        
        # Tags frame
        self.tags_frame = ttk.Frame(self)
        self.tags_frame.pack(fill='x', pady=5, padx=(95, 0))
        
        self.answers = []
    
    def add_answer(self, value: str = None):
        """Add an answer tag."""
        if value is None:
            value = self.add_entry.get().strip()
            self.add_entry.delete(0, tk.END)
        
        if not value or value in self.answers:
            return
        
        self.answers.append(value)
        self._refresh_tags()
    
    def _refresh_tags(self):
        """Refresh the tag display."""
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        for answer in self.answers:
            tag = ttk.Frame(self.tags_frame, style='Tag.TFrame')
            tag.pack(side='left', padx=2, pady=2)
            
            ttk.Label(tag, text=answer, background='#e0e7ff', padding=(5, 2)).pack(side='left')
            
            def remove(a=answer):
                self.answers.remove(a)
                self._refresh_tags()
            
            btn = ttk.Button(tag, text="×", width=2, command=remove)
            btn.pack(side='left')
    
    def get(self) -> List[str]:
        return self.answers.copy()
    
    def set(self, answers: List[str]):
        self.answers = list(answers or [])
        self._refresh_tags()


class TokensEditor(ttk.Frame):
    """Widget for editing ordered tokens (for word order exercises)."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text="Tokens (in order):", width=15, anchor='e').pack(side='left')
        
        self.add_entry = ttk.Entry(header, width=20)
        self.add_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.add_entry.bind('<Return>', lambda e: self.add_token())
        
        ttk.Button(header, text="+ Add", command=self.add_token, width=8).pack(side='left')
        
        # Tokens frame
        self.tokens_frame = ttk.Frame(self)
        self.tokens_frame.pack(fill='x', pady=5, padx=(95, 0))
        
        self.tokens = []
    
    def add_token(self, value: str = None):
        if value is None:
            value = self.add_entry.get().strip()
            self.add_entry.delete(0, tk.END)
        
        if not value:
            return
        
        self.tokens.append(value)
        self._refresh()
    
    def _refresh(self):
        for widget in self.tokens_frame.winfo_children():
            widget.destroy()
        
        for i, token in enumerate(self.tokens):
            tag = ttk.Frame(self.tokens_frame)
            tag.pack(side='left', padx=2, pady=2)
            
            ttk.Label(tag, text=f"{i+1}.", foreground='gray').pack(side='left')
            ttk.Label(tag, text=token, background='#fce7f3', padding=(5, 2)).pack(side='left')
            
            def remove(t=token):
                self.tokens.remove(t)
                self._refresh()
            
            ttk.Button(tag, text="×", width=2, command=remove).pack(side='left')
    
    def get(self) -> List[str]:
        return self.tokens.copy()
    
    def set(self, tokens: List[str]):
        self.tokens = list(tokens or [])
        self._refresh()


class MatchPairsEditor(ttk.Frame):
    """Widget for editing match pairs."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text="Match Pairs:", font=('', 10, 'bold')).pack(side='left')
        ttk.Button(header, text="+ Add Pair", command=self.add_pair).pack(side='right')
        
        # Pairs frame
        self.pairs_frame = ttk.Frame(self)
        self.pairs_frame.pack(fill='x', pady=5)
        
        self.pair_entries = []
    
    def add_pair(self, left: str = "", right: str = ""):
        row = ttk.Frame(self.pairs_frame)
        row.pack(fill='x', pady=3)
        
        ttk.Label(row, text="Left:", width=8).pack(side='left')
        left_entry = ttk.Entry(row, width=25)
        left_entry.pack(side='left', padx=5)
        left_entry.insert(0, left)
        
        ttk.Label(row, text="↔").pack(side='left', padx=10)
        
        ttk.Label(row, text="Right:").pack(side='left')
        right_entry = ttk.Entry(row, width=25)
        right_entry.pack(side='left', padx=5)
        right_entry.insert(0, right)
        
        def remove():
            self.pair_entries.remove((row, left_entry, right_entry))
            row.destroy()
        
        ttk.Button(row, text="×", width=2, command=remove).pack(side='left', padx=5)
        self.pair_entries.append((row, left_entry, right_entry))
    
    def get(self) -> List[Dict[str, str]]:
        return [
            {'left': l.get(), 'right': r.get()}
            for _, l, r in self.pair_entries
            if l.get().strip() or r.get().strip()
        ]
    
    def set(self, pairs: List[Dict[str, str]]):
        for row, _, _ in self.pair_entries:
            row.destroy()
        self.pair_entries = []
        
        for pair in (pairs or []):
            self.add_pair(pair.get('left', ''), pair.get('right', ''))


# =============================================================================
# Step Editor Frames
# =============================================================================

class BaseStepEditor(ttk.Frame):
    """Base class for step editors."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, **kwargs)
        self.step_data = step_data
    
    def get_data(self) -> Dict:
        """Override to return step data."""
        return {}
    
    def create_labeled_entry(self, parent, label: str, key: str, width: int = 40) -> ttk.Entry:
        """Create a labeled entry field."""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=3)
        
        ttk.Label(frame, text=label, width=15, anchor='e').pack(side='left', padx=(0, 5))
        entry = ttk.Entry(frame, width=width)
        entry.pack(side='left', fill='x', expand=True)
        entry.insert(0, str(self.step_data.get(key, '')))
        
        return entry
    
    def create_labeled_text(self, parent, label: str, key: str, height: int = 5) -> scrolledtext.ScrolledText:
        """Create a labeled text area."""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=3)
        
        ttk.Label(frame, text=label, width=15, anchor='ne').pack(side='left', padx=(0, 5))
        text = scrolledtext.ScrolledText(frame, width=50, height=height, wrap=tk.WORD)
        text.pack(side='left', fill='x', expand=True)
        text.insert('1.0', str(self.step_data.get(key, '')))
        
        return text


class MarkdownStepEditor(BaseStepEditor):
    """Editor for markdown steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.markdown_text = self.create_labeled_text(self, "Markdown:", 'markdown', height=10)
        
        self.images_editor = ImageListEditor(self)
        self.images_editor.pack(fill='x', pady=5)
        self.images_editor.set(step_data.get('images', []))
    
    def get_data(self) -> Dict:
        return {
            'markdown': self.markdown_text.get('1.0', tk.END).rstrip(),
            'images': self.images_editor.get(),
        }


class IntroduceWordStepEditor(BaseStepEditor):
    """Editor for introduce_word steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.word_entry = self.create_labeled_entry(self, "Word (Bernese):", 'word')
        
        # Translations
        trans = step_data.get('translation', {})
        
        frame = ttk.Frame(self)
        frame.pack(fill='x', pady=3)
        ttk.Label(frame, text="English:", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.en_entry = ttk.Entry(frame, width=30)
        self.en_entry.pack(side='left')
        self.en_entry.insert(0, trans.get('en', ''))
        
        ttk.Label(frame, text="German:").pack(side='left', padx=(15, 5))
        self.de_entry = ttk.Entry(frame, width=30)
        self.de_entry.pack(side='left')
        self.de_entry.insert(0, trans.get('de', ''))
        
        # Audio
        self.audio_entry = FilePathEntry(self, "Audio:", 'audio')
        self.audio_entry.pack(fill='x', pady=3)
        self.audio_entry.set(step_data.get('audio', ''))
        
        # Images
        self.images_editor = ImageListEditor(self)
        self.images_editor.pack(fill='x', pady=5)
        self.images_editor.set(step_data.get('images', []))
    
    def get_data(self) -> Dict:
        return {
            'word': self.word_entry.get(),
            'translation': {
                'en': self.en_entry.get(),
                'de': self.de_entry.get(),
            },
            'audio': self.audio_entry.get(),
            'images': self.images_editor.get(),
        }


class ClozeStepEditor(BaseStepEditor):
    """Editor for cloze (fill-in-the-blank) steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Sentence
        sentence = step_data.get('sentence', {})
        
        frame1 = ttk.Frame(self)
        frame1.pack(fill='x', pady=3)
        ttk.Label(frame1, text="Question (EN):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.question_entry = ttk.Entry(frame1, width=50)
        self.question_entry.pack(side='left', fill='x', expand=True)
        self.question_entry.insert(0, sentence.get('question', ''))
        
        frame2 = ttk.Frame(self)
        frame2.pack(fill='x', pady=3)
        ttk.Label(frame2, text="Helper (DE):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.helper_entry = ttk.Entry(frame2, width=50)
        self.helper_entry.pack(side='left', fill='x', expand=True)
        self.helper_entry.insert(0, sentence.get('helper', ''))
        
        # Target (before blank, after blank)
        target = sentence.get('target', ['', ''])
        frame3 = ttk.Frame(self)
        frame3.pack(fill='x', pady=3)
        ttk.Label(frame3, text="Before blank:", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.before_entry = ttk.Entry(frame3, width=20)
        self.before_entry.pack(side='left')
        self.before_entry.insert(0, target[0] if len(target) > 0 else '')
        
        ttk.Label(frame3, text="After blank:").pack(side='left', padx=(15, 5))
        self.after_entry = ttk.Entry(frame3, width=20)
        self.after_entry.pack(side='left')
        self.after_entry.insert(0, target[1] if len(target) > 1 else '')
        
        # Audio
        self.audio_entry = FilePathEntry(self, "Audio:", 'audio')
        self.audio_entry.pack(fill='x', pady=3)
        self.audio_entry.set(step_data.get('audio', ''))

        # Answers
        self.answers_editor = AnswersEditor(self)
        self.answers_editor.pack(fill='x', pady=5)
        self.answers_editor.set(step_data.get('answers', []))
        
        # Solution display
        self.solution_text = self.create_labeled_text(self, "Solution text:", 'solution_display', height=4)
        
        # Images
        self.images_editor = ImageListEditor(self)
        self.images_editor.pack(fill='x', pady=5)
        self.images_editor.set(step_data.get('images', []))
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'sentence': {
                'question': self.question_entry.get(),
                'helper': self.helper_entry.get(),
                'target': [self.before_entry.get(), self.after_entry.get()],
            },
            'answers': self.answers_editor.get(),
            'solution_display': self.solution_text.get('1.0', tk.END).rstrip(),
            'images': self.images_editor.get(),
        }


class OrderStepEditor(BaseStepEditor):
    """Editor for word order steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Sentence
        sentence = step_data.get('sentence', {})
        
        frame1 = ttk.Frame(self)
        frame1.pack(fill='x', pady=3)
        ttk.Label(frame1, text="Question (EN):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.question_entry = ttk.Entry(frame1, width=50)
        self.question_entry.pack(side='left', fill='x', expand=True)
        self.question_entry.insert(0, sentence.get('question', ''))
        
        frame2 = ttk.Frame(self)
        frame2.pack(fill='x', pady=3)
        ttk.Label(frame2, text="Helper (DE):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.helper_entry = ttk.Entry(frame2, width=50)
        self.helper_entry.pack(side='left', fill='x', expand=True)
        self.helper_entry.insert(0, sentence.get('helper', ''))

        # Tokens
        self.tokens_editor = TokensEditor(self)
        self.tokens_editor.pack(fill='x', pady=5)
        self.tokens_editor.set(step_data.get('tokens', []))
        
        # Audio
        self.audio_entry = FilePathEntry(self, "Audio:", 'audio')
        self.audio_entry.pack(fill='x', pady=3)
        self.audio_entry.set(step_data.get('audio', ''))

        # Solution display
        self.solution_text = self.create_labeled_text(self, "Solution text:", 'solution_display', height=4)
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'sentence': {
                'question': self.question_entry.get(),
                'helper': self.helper_entry.get(),
            },
            'tokens': self.tokens_editor.get(),
            'solution_display': self.solution_text.get('1.0', tk.END).rstrip(),
        }


class TranslateTypeStepEditor(BaseStepEditor):
    """Editor for translate_type steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Sentence
        sentence = step_data.get('sentence', {})
        
        frame1 = ttk.Frame(self)
        frame1.pack(fill='x', pady=3)
        ttk.Label(frame1, text="Question (EN):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.question_entry = ttk.Entry(frame1, width=50)
        self.question_entry.pack(side='left', fill='x', expand=True)
        self.question_entry.insert(0, sentence.get('question', ''))
        
        frame2 = ttk.Frame(self)
        frame2.pack(fill='x', pady=3)
        ttk.Label(frame2, text="Helper (DE):", width=15, anchor='e').pack(side='left', padx=(0, 5))
        self.helper_entry = ttk.Entry(frame2, width=50)
        self.helper_entry.pack(side='left', fill='x', expand=True)
        self.helper_entry.insert(0, sentence.get('helper', ''))
        
        # Answers
        self.answers_editor = AnswersEditor(self)
        self.answers_editor.pack(fill='x', pady=5)
        self.answers_editor.set(step_data.get('answers', []))
        
        # Solution display
        self.solution_text = self.create_labeled_text(self, "Solution text:", 'solution_display', height=4)
        
        # Images
        self.images_editor = ImageListEditor(self)
        self.images_editor.pack(fill='x', pady=5)
        self.images_editor.set(step_data.get('images', []))
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'sentence': {
                'question': self.question_entry.get(),
                'helper': self.helper_entry.get(),
            },
            'answers': self.answers_editor.get(),
            'solution_display': self.solution_text.get('1.0', tk.END).rstrip(),
            'images': self.images_editor.get(),
        }


class ListenTypeStepEditor(BaseStepEditor):
    """Editor for listen_type steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Audio
        self.audio_entry = FilePathEntry(self, "Audio:", 'audio')
        self.audio_entry.pack(fill='x', pady=3)
        self.audio_entry.set(step_data.get('audio', ''))
        
        # Answers
        self.answers_editor = AnswersEditor(self)
        self.answers_editor.pack(fill='x', pady=5)
        self.answers_editor.set(step_data.get('answers', []))
        
        # Solution display
        self.solution_text = self.create_labeled_text(self, "Solution text:", 'solution_display', height=4)
        
        # Images
        self.images_editor = ImageListEditor(self)
        self.images_editor.pack(fill='x', pady=5)
        self.images_editor.set(step_data.get('images', []))
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'audio': self.audio_entry.get(),
            'answers': self.answers_editor.get(),
            'solution_display': self.solution_text.get('1.0', tk.END).rstrip(),
            'images': self.images_editor.get(),
        }


class TrueFalseStepEditor(BaseStepEditor):
    """Editor for true_false steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Audio
        self.audio_entry = FilePathEntry(self, "Audio:", 'audio')
        self.audio_entry.pack(fill='x', pady=3)
        self.audio_entry.set(step_data.get('audio', ''))
        
        # Statement text
        self.text_entry = self.create_labeled_entry(self, "Statement:", 'text', width=50)
        
        # Answer
        frame = ttk.Frame(self)
        frame.pack(fill='x', pady=3)
        ttk.Label(frame, text="Correct answer:", width=15, anchor='e').pack(side='left', padx=(0, 5))
        
        self.answer_var = tk.StringVar(value=step_data.get('answer', 'True'))
        ttk.Radiobutton(frame, text="True", variable=self.answer_var, value="True").pack(side='left', padx=10)
        ttk.Radiobutton(frame, text="False", variable=self.answer_var, value="False").pack(side='left', padx=10)
        
        # Solution display
        self.solution_text = self.create_labeled_text(self, "Solution text:", 'solution_display', height=4)
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'audio': self.audio_entry.get(),
            'text': self.text_entry.get(),
            'answer': self.answer_var.get(),
            'solution_display': self.solution_text.get('1.0', tk.END).rstrip(),
        }


class MatchStepEditor(BaseStepEditor):
    """Editor for match steps."""
    
    def __init__(self, parent, step_data: Dict, **kwargs):
        super().__init__(parent, step_data, **kwargs)
        
        self.prompt_entry = self.create_labeled_entry(self, "Prompt:", 'prompt')
        
        # Pairs
        self.pairs_editor = MatchPairsEditor(self)
        self.pairs_editor.pack(fill='x', pady=5)
        self.pairs_editor.set(step_data.get('pairs', []))
    
    def get_data(self) -> Dict:
        return {
            'prompt': self.prompt_entry.get(),
            'pairs': self.pairs_editor.get(),
        }


# Step editor factory
STEP_EDITORS = {
    'markdown': MarkdownStepEditor,
    'introduce_word': IntroduceWordStepEditor,
    'cloze': ClozeStepEditor,
    'order': OrderStepEditor,
    'translate_type': TranslateTypeStepEditor,
    'listen_type': ListenTypeStepEditor,
    'true_false': TrueFalseStepEditor,
    'match': MatchStepEditor,
}


# =============================================================================
# Step Card Widget
# =============================================================================

class StepCard(ttk.Frame):
    """A collapsible card for a single step."""
    
    def __init__(self, parent, step_data: Dict, index: int, 
                 on_move_up, on_move_down, on_delete, on_update_id, **kwargs):
        super().__init__(parent, **kwargs)
        
        # IMPORTANT: Make a deep copy to avoid reference issues
        self.step_data = deepcopy(step_data)
        self.index = index
        self.expanded = False
        self.editor = None
        
        # Callbacks
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_delete = on_delete
        self.on_update_id = on_update_id
        
        self.configure(relief='solid', borderwidth=1)
        
        # Header
        self.header = ttk.Frame(self)
        self.header.pack(fill='x', padx=5, pady=5)
        
        # Step number
        ttk.Label(self.header, text=f"#{index + 1}", font=('', 10, 'bold'), width=4).pack(side='left')
        
        # Type badge
        step_type = step_data.get('type', 'markdown')
        type_label = STEP_TYPES.get(step_type, step_type)
        badge = ttk.Label(self.header, text=type_label, background='#6366f1', foreground='white', padding=(5, 2))
        badge.pack(side='left', padx=5)
        
        # ID entry
        ttk.Label(self.header, text="ID:").pack(side='left', padx=(10, 2))
        self.id_entry = ttk.Entry(self.header, width=25)
        self.id_entry.pack(side='left')
        self.id_entry.insert(0, step_data.get('id', ''))
        self.id_entry.bind('<FocusOut>', lambda e: self._update_id())
        self.id_entry.bind('<KeyRelease>', lambda e: self._update_id())
        
        # Buttons
        btn_frame = ttk.Frame(self.header)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="↑", width=3, command=lambda: self.on_move_up(self.index)).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="↓", width=3, command=lambda: self.on_move_down(self.index)).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="🗑", width=3, command=lambda: self.on_delete(self.index)).pack(side='left', padx=1)
        
        self.expand_btn = ttk.Button(btn_frame, text="▼ Edit", width=8, command=self.toggle_expand)
        self.expand_btn.pack(side='left', padx=(5, 0))
        
        # Body (editor)
        self.body = ttk.Frame(self)
    
    def _update_id(self):
        """Update the step_data id and notify parent."""
        self.step_data['id'] = self.id_entry.get()
        self.on_update_id(self.index, self.id_entry.get())
    
    def toggle_expand(self):
        """Toggle the expanded state."""
        if self.expanded:
            # Collapsing - save data first
            self.expand_btn.configure(text="▼ Edit")
            if self.editor:
                # Save data from editor to step_data
                data = self.editor.get_data()
                self.step_data.update(data)
                self.editor.destroy()
                self.editor = None
            self.body.pack_forget()
            self.expanded = False
        else:
            # Expanding
            self.expand_btn.configure(text="▲ Close")
            self.body.pack(fill='x', padx=10, pady=(0, 10))
            
            # Create editor with current step_data
            step_type = self.step_data.get('type', 'markdown')
            editor_class = STEP_EDITORS.get(step_type, MarkdownStepEditor)
            self.editor = editor_class(self.body, self.step_data)
            self.editor.pack(fill='x')
            self.expanded = True
    
    def save_data(self):
        """Save data from editor to step_data."""
        if self.editor:
            data = self.editor.get_data()
            self.step_data.update(data)
        self.step_data['id'] = self.id_entry.get()
    
    def get_data(self) -> Dict:
        """Get the complete step data."""
        self.save_data()
        return deepcopy(self.step_data)


# =============================================================================
# Main Application
# =============================================================================

class LessonEditorApp:
    """Main application class."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bärndütsch Lesson Editor")
        self.root.geometry("900x700")
        
        # Current file path for auto-save
        self.current_filepath = None
        
        # Lesson data
        self.lesson = {
            'id': '',
            'title': '',
            'description': '',
            'estimated_minutes': 10,
            'section': 'Basics',
            'steps': []
        }
        
        self.step_cards = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the main UI."""
        # Configure styles
        style = ttk.Style()
        style.configure('Header.TLabel', font=('', 12, 'bold'))
        style.configure('Title.TLabel', font=('', 16, 'bold'))
        
        # Main container
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill='both', expand=True)
        
        # ===== Header Section =====
        header_frame = ttk.LabelFrame(main, text="Lesson Details", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1: ID Number, ID Slug, and Title
        row1 = ttk.Frame(header_frame)
        row1.pack(fill='x', pady=3)
        
        ttk.Label(row1, text="ID:", width=12, anchor='e').pack(side='left')
        
        # ID number spinbox
        self.id_num_spin = ttk.Spinbox(row1, from_=1, to=99, width=3, format="%02.0f")
        self.id_num_spin.pack(side='left', padx=(5, 0))
        self.id_num_spin.set("01")
        self.id_num_spin.bind('<KeyRelease>', self._on_id_change)
        self.id_num_spin.bind('<<Increment>>', self._on_id_change)
        self.id_num_spin.bind('<<Decrement>>', self._on_id_change)
        
        ttk.Label(row1, text="_").pack(side='left')
        
        # ID slug entry
        self.id_slug_entry = ttk.Entry(row1, width=25)
        self.id_slug_entry.pack(side='left', padx=(0, 5))
        self.id_slug_entry.bind('<KeyRelease>', self._on_id_change)
        
        ttk.Label(row1, text="Title:").pack(side='left', padx=(20, 0))
        self.title_entry = ttk.Entry(row1, width=40)
        self.title_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.title_entry.bind('<KeyRelease>', self._on_title_change)
        
        # Row 2: Description
        row2 = ttk.Frame(header_frame)
        row2.pack(fill='x', pady=3)
        
        ttk.Label(row2, text="Description:", width=12, anchor='e').pack(side='left')
        self.desc_entry = ttk.Entry(row2, width=70)
        self.desc_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Row 3: Minutes and Section
        row3 = ttk.Frame(header_frame)
        row3.pack(fill='x', pady=3)
        
        ttk.Label(row3, text="Est. Minutes:", width=12, anchor='e').pack(side='left')
        self.minutes_spin = ttk.Spinbox(row3, from_=1, to=60, width=5)
        self.minutes_spin.pack(side='left', padx=5)
        self.minutes_spin.set(10)
        
        ttk.Label(row3, text="Section:").pack(side='left', padx=(20, 0))
        self.section_combo = ttk.Combobox(row3, values=SECTIONS, width=15)
        self.section_combo.pack(side='left', padx=5)
        self.section_combo.set('Basics')
        
        # ===== Toolbar =====
        toolbar = ttk.Frame(main)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(toolbar, text="📂 Load YAML", command=self.load_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="💾 Export YAML", command=self.export_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="👁 Preview", command=self.preview_yaml).pack(side='left', padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Auto-save indicator
        self.autosave_label = ttk.Label(toolbar, text="", foreground='gray')
        self.autosave_label.pack(side='left', padx=5)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        ttk.Label(toolbar, text="Add Step:").pack(side='left', padx=(0, 5))
        self.step_type_combo = ttk.Combobox(toolbar, values=list(STEP_TYPES.values()), width=20)
        self.step_type_combo.pack(side='left')
        self.step_type_combo.current(0)
        ttk.Button(toolbar, text="+ Add", command=self.add_step).pack(side='left', padx=5)
        
        # ===== Steps Section =====
        steps_label = ttk.Frame(main)
        steps_label.pack(fill='x', pady=5)
        ttk.Label(steps_label, text="Lesson Steps", style='Header.TLabel').pack(side='left')
        self.steps_count_label = ttk.Label(steps_label, text="(0 steps)")
        self.steps_count_label.pack(side='left', padx=10)
        
        # Scrollable steps container
        self.steps_container = ScrollableFrame(main)
        self.steps_container.pack(fill='both', expand=True)
    
    def _get_full_id(self) -> str:
        """Get the full ID from number and slug."""
        num = self.id_num_spin.get().zfill(2)
        slug = self.id_slug_entry.get()
        if slug:
            return f"{num}_{slug}"
        return num
    
    def _set_id_from_full(self, full_id: str):
        """Set the number and slug from a full ID."""
        if not full_id:
            self.id_num_spin.set("01")
            self.id_slug_entry.delete(0, tk.END)
            return
        
        # Try to parse as "NN_slug" format
        match = re.match(r'^(\d+)_(.*)$', full_id)
        if match:
            self.id_num_spin.set(match.group(1).zfill(2))
            self.id_slug_entry.delete(0, tk.END)
            self.id_slug_entry.insert(0, match.group(2))
        else:
            # No number prefix, just use as slug
            self.id_num_spin.set("01")
            self.id_slug_entry.delete(0, tk.END)
            self.id_slug_entry.insert(0, full_id)
    
    def _on_id_change(self, event=None):
        """Handle ID change."""
        # Update lesson data
        self.lesson['id'] = self._get_full_id()
    
    def _on_title_change(self, event=None):
        """Auto-generate slug from title."""
        title = self.title_entry.get()
        current_slug = self.id_slug_entry.get()
        
        # Only auto-generate if slug is empty or looks auto-generated
        if not current_slug or current_slug == slugify(current_slug):
            new_slug = slugify(title)
            self.id_slug_entry.delete(0, tk.END)
            self.id_slug_entry.insert(0, new_slug)
            self._on_id_change()
    
    def _refresh_steps_ui(self):
        """Refresh the steps UI from lesson data."""
        # Clear existing cards
        for card in self.step_cards:
            card.destroy()
        self.step_cards = []
        
        # Create new cards
        for i, step in enumerate(self.lesson['steps']):
            card = StepCard(
                self.steps_container.scrollable_frame,
                step,
                i,
                on_move_up=self.move_step_up,
                on_move_down=self.move_step_down,
                on_delete=self.delete_step,
                on_update_id=self.update_step_id,
            )
            card.pack(fill='x', pady=3)
            self.step_cards.append(card)
        
        self.steps_count_label.configure(text=f"({len(self.lesson['steps'])} steps)")
    
    def _collect_all_data(self):
        """Collect all data from UI into lesson dict."""
        self.lesson['id'] = self._get_full_id()
        self.lesson['title'] = self.title_entry.get()
        self.lesson['description'] = self.desc_entry.get()
        self.lesson['estimated_minutes'] = int(self.minutes_spin.get())
        self.lesson['section'] = self.section_combo.get()
        
        # Collect step data from cards
        new_steps = []
        for card in self.step_cards:
            new_steps.append(card.get_data())
        self.lesson['steps'] = new_steps
    
    def _auto_save(self):
        """Auto-save if a file is currently loaded."""
        if self.current_filepath:
            try:
                self._collect_all_data()
                yaml_content = export_to_yaml(self.lesson)
                with open(self.current_filepath, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                self.autosave_label.configure(text=f"Auto-saved ✓")
                # Clear the message after 2 seconds
                self.root.after(2000, lambda: self.autosave_label.configure(text=""))
            except Exception as e:
                self.autosave_label.configure(text=f"Auto-save failed!")
    
    def add_step(self):
        """Add a new step."""
        # First, collect all current data to preserve it
        self._collect_all_data()
        
        type_label = self.step_type_combo.get()
        step_type = next((k for k, v in STEP_TYPES.items() if v == type_label), 'markdown')
        
        new_step = {
            'type': step_type,
            'id': f"{step_type}_{len(self.lesson['steps'])}",
        }
        
        # Add type-specific defaults
        if step_type == 'markdown':
            new_step['markdown'] = ''
            new_step['images'] = []
        elif step_type == 'introduce_word':
            new_step['word'] = ''
            new_step['translation'] = {'en': '', 'de': ''}
            new_step['audio'] = ''
            new_step['images'] = []
        elif step_type == 'cloze':
            new_step['prompt'] = 'Fill in the missing words (answer in Bärndütsch).'
            new_step['sentence'] = {'question': '', 'helper': '', 'target': ['', '']}
            new_step['answers'] = []
            new_step['solution_display'] = ''
            new_step['audio'] = ''
            new_step['images'] = []
        elif step_type == 'order':
            new_step['prompt'] = 'Put the words in the correct order (Bärndütsch).'
            new_step['sentence'] = {'question': '', 'helper': ''}
            new_step['tokens'] = []
            new_step['audio'] = ''
            new_step['solution_display'] = ''
        elif step_type == 'translate_type':
            new_step['prompt'] = 'Translate the following Sentence.'
            new_step['sentence'] = {'question': '', 'helper': ''}
            new_step['answers'] = []
            new_step['solution_display'] = ''
            new_step['images'] = []
        elif step_type == 'listen_type':
            new_step['prompt'] = 'Listen and type what you hear (Bärndütsch).'
            new_step['audio'] = ''
            new_step['answers'] = []
            new_step['solution_display'] = ''
            new_step['images'] = []
        elif step_type == 'true_false':
            new_step['prompt'] = 'What do you think is said?'
            new_step['audio'] = ''
            new_step['text'] = ''
            new_step['answer'] = 'True'
            new_step['solution_display'] = ''
        elif step_type == 'match':
            new_step['prompt'] = 'Match the translations (English → Bärndütsch).'
            new_step['pairs'] = []
        
        self.lesson['steps'].append(new_step)
        self._refresh_steps_ui()
        
        # Auto-save after adding step
        self._auto_save()
    
    def move_step_up(self, index: int):
        """Move a step up."""
        if index > 0:
            self._collect_all_data()
            steps = self.lesson['steps']
            steps[index], steps[index - 1] = steps[index - 1], steps[index]
            self._refresh_steps_ui()
    
    def move_step_down(self, index: int):
        """Move a step down."""
        if index < len(self.lesson['steps']) - 1:
            self._collect_all_data()
            steps = self.lesson['steps']
            steps[index], steps[index + 1] = steps[index + 1], steps[index]
            self._refresh_steps_ui()
    
    def delete_step(self, index: int):
        """Delete a step."""
        if messagebox.askyesno("Delete Step", f"Are you sure you want to delete step #{index + 1}?"):
            self._collect_all_data()
            del self.lesson['steps'][index]
            self._refresh_steps_ui()
    
    def update_step_id(self, index: int, new_id: str):
        """Update a step's ID."""
        if index < len(self.lesson['steps']):
            self.lesson['steps'][index]['id'] = new_id
    
    def load_file(self):
        """Load a YAML file."""
        filepath = filedialog.askopenfilename(
            title="Open Lesson YAML",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            self.lesson = load_yaml(filepath)
            self.current_filepath = filepath  # Enable auto-save
            
            # Update UI
            self._set_id_from_full(self.lesson.get('id', ''))
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.lesson.get('title', ''))
            
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, self.lesson.get('description', ''))
            
            self.minutes_spin.delete(0, tk.END)
            self.minutes_spin.insert(0, str(self.lesson.get('estimated_minutes', 10)))
            
            self.section_combo.set(self.lesson.get('section', 'Basics'))
            
            # Ensure steps is a list
            if 'steps' not in self.lesson or self.lesson['steps'] is None:
                self.lesson['steps'] = []
            
            self._refresh_steps_ui()
            
            messagebox.showinfo("Success", f"Loaded {len(self.lesson['steps'])} steps from {os.path.basename(filepath)}")
            self.autosave_label.configure(text=f"Editing: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def export_file(self):
        """Export to YAML file."""
        self._collect_all_data()
        
        # Default filename from ID
        default_name = f"{self.lesson['id']}.yaml" if self.lesson['id'] else "lesson.yaml"
        
        filepath = filedialog.asksaveasfilename(
            title="Save Lesson YAML",
            defaultextension=".yaml",
            initialfile=default_name,
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            yaml_content = export_to_yaml(self.lesson)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            self.current_filepath = filepath  # Enable auto-save for this file
            messagebox.showinfo("Success", f"Saved to {os.path.basename(filepath)}")
            self.autosave_label.configure(text=f"Editing: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def preview_yaml(self):
        """Show YAML preview in a popup window."""
        self._collect_all_data()
        yaml_content = export_to_yaml(self.lesson)
        
        # Create popup window
        preview = tk.Toplevel(self.root)
        preview.title("YAML Preview")
        preview.geometry("700x600")
        
        # Text widget with YAML content
        text = scrolledtext.ScrolledText(preview, wrap=tk.NONE, font=('Consolas', 10))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert('1.0', yaml_content)
        text.configure(state='disabled')
        
        # Copy button
        def copy_to_clipboard():
            preview.clipboard_clear()
            preview.clipboard_append(yaml_content)
            messagebox.showinfo("Copied", "YAML copied to clipboard!")
        
        ttk.Button(preview, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=10)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    root = tk.Tk()
    
    # Set a nicer theme if available
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        pass
    
    app = LessonEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()