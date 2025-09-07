# Design Decisions

This document captures important design decisions made during the development of PicTex. It serves as a reference for maintaining consistency and understanding the rationale behind non-obvious behaviors.

## Text Wrapping and Sizing Behavior

### Decision: TextNode with `auto` width fits wrapped content, not container width

**Context:**
When implementing text wrapping, a question arose about how a TextNode should behave when:
- It has `width: auto` (default behavior)  
- It's placed in a container with fixed width
- Text wrapping occurs due to width constraints

**The Question:**
Should the TextNode:
A) Expand to fill the full available width (like CSS), or  
B) Shrink to fit the actual wrapped text content?

**Decision: Option B** - TextNode fits the wrapped text content

**Rationale:**
1. **Consistency with PicTex's sizing system**: `auto` → `fit-content` is the documented behavior throughout the library
2. **Predictable behavior**: "Use only the space you need" is clearer than context-dependent sizing
3. **User control**: Users can explicitly use `.size(width="100%")` when they want full-width behavior
4. **Flexibility**: Both behaviors are achievable with clear, explicit syntax

**Examples:**

```python
# Current behavior (fits content):
Text("Long text that wraps").padding(10)  # TextNode width = wrapped text width

# Full-width behavior (explicit):  
Text("Long text that wraps").size(width="100%").padding(10)  # TextNode width = container width
```

**Workaround:**
Users wanting CSS-like behavior can use `.size(width="100%")` on the TextNode.

**Alternative Considered:**
Making TextNode expand to container width by default was rejected because:
- It would break consistency with the `auto` sizing behavior
- It would be a special case that users might not expect
- The explicit approach is clearer and more maintainable

---

## Text Wrapping Width Calculation

### Decision: TextShaper receives content area width, not total element width

**Context:**
When implementing text wrapping, we needed to determine what width constraint to pass to the TextShaper.

**The Question:**
Should TextShaper receive:
A) The total width constraint of the TextNode, or  
B) The content area width (after subtracting padding/border)?

**Decision: Option B** - Content area width

**Rationale:**
1. **Follows border-box model**: In PicTex, `size()` includes padding and border
2. **Correct text layout**: Text should wrap within the actual content area
3. **Consistent with web standards**: Similar to how CSS text wrapping works

**Implementation:**
```python
def _get_text_wrap_width(self) -> Optional[float]:
    if self.constraints.has_width_constraint():
        total_width = self.constraints.get_effective_width()
        
        # Subtract TextNode's own padding and border
        padding = self.computed_styles.padding.get()
        border = self.computed_styles.border.get()
        border_width = border.width if border else 0
        
        horizontal_spacing = padding.left + padding.right + (border_width * 2)
        content_width = total_width - horizontal_spacing
        
        return max(0, content_width)
```

**Example Calculation:**
- Container width: 250px, padding: 10px → Available for TextNode: 230px
- TextNode padding: 8px → Available for text content: 214px
- TextShaper receives: 214px ✓

---

## Text Wrapping and Positioning Interaction

### Decision: Positioned elements automatically disable text wrapping

**Context:**
TextNodes can have both text wrapping enabled and positioning applied. This creates a conceptual question about how these features should interact.

**The Question:**
Should a TextNode with `position()` set:
A) Still perform text wrapping based on some constraint, or  
B) Automatically behave as `text-wrap: nowrap`?

**Decision: Option B** - Positioned elements disable text wrapping

**Rationale:**
1. **Conceptual clarity**: Positioned elements exist outside the normal layout flow where text wrapping constraints are defined
2. **Avoids ambiguity**: Without a parent container's layout context, there's no clear width constraint for wrapping
3. **Consistent with CSS behavior**: Absolutely positioned elements need explicit width to wrap text
4. **Predictable behavior**: Users expect positioned elements to have full control over their content layout

**Implementation:**
```python
def _get_text_wrap_width(self) -> Optional[float]:
    # If element has positioning, disable text wrapping
    position_style = self.computed_styles.position.get()
    if position_style is not None:
        return None
```

**Examples:**
```python
# This text will NOT wrap, regardless of length
positioned_text = Text("Very long text").position(x=100, y=50)

# This text WILL wrap within container constraints
normal_text = Text("Very long text")  # No positioning
```

**Alternative Considered:**
Allowing positioned text to wrap was rejected because:
- It would require arbitrary constraint definition
- The interaction would be unpredictable
- It conflicts with the semantic meaning of positioning

---

## Future Considerations

### Potential Features for Advanced Users

If the current text sizing behavior becomes a frequent pain point, consider:

1. **Text sizing mode**: A style property like `text-size-mode: "fit-content" | "fill-available"`
2. **Container queries**: More sophisticated constraint resolution
3. **Advanced text layout**: Additional text wrapping modes

These would be additive features that don't break current behavior.

---

## Contributing to This Document

When making significant design decisions:

1. Document the decision with context and rationale
2. Include examples of the chosen behavior
3. Note alternatives considered and why they were rejected
4. Consider future implications and potential extensions