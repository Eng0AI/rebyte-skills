# Typeform-Style Theme

## CSS Theme Override

Add this CSS after the Forms.md stylesheet to achieve a Typeform-like appearance:

```css
/* Typeform-Style Theme for Forms.md */

.fmd-root {
  /* Typography - Large, bold questions */
  --fmd-form-question-font-size: 28px;
  --fmd-form-question-font-size-xs: 22px;
  --fmd-font-size-base: 18px;
  --fmd-heading-font-weight: 500;

  /* Smoother, slower transitions */
  --fmd-slide-transition-duration: 400ms;

  /* Pill-shaped buttons */
  --fmd-border-radius: 24px;
  --fmd-border-radius-lg: 32px;
  --fmd-action-border-radius: 24px;

  /* Generous spacing */
  --fmd-spacer: 24px;
  --fmd-content-padding-x: 48px;
  --fmd-content-padding-top: 64px;
  --fmd-form-field-padding-y: 16px;

  /* Narrower content for focus */
  --fmd-main-container-width: 640px;
}

/* Minimal, underline-style inputs */
.fmd-root .fmd-form-control {
  border: none;
  border-bottom: 2px solid rgba(var(--fmd-body-color-rgb), 0.3);
  border-radius: 0;
  background: transparent;
  font-size: 1.25em;
  padding: 12px 0;
  transition: border-color 0.2s ease;
}

.fmd-root .fmd-form-control:focus {
  border-bottom-color: rgb(var(--fmd-accent-rgb));
  box-shadow: none;
  outline: none;
}

/* Larger, more prominent buttons */
.fmd-root .fmd-btn {
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 600;
  min-width: 140px;
}

/* Choice inputs - card style */
.fmd-root .fmd-form-check-label {
  padding: 16px 20px;
  border: 2px solid rgba(var(--fmd-body-color-rgb), 0.15);
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.fmd-root .fmd-form-check-input:checked + .fmd-form-check-label {
  border-color: rgb(var(--fmd-accent-rgb));
  background: rgba(var(--fmd-accent-rgb), 0.08);
}

.fmd-root .fmd-form-check-label:hover {
  border-color: rgba(var(--fmd-accent-rgb), 0.5);
}

/* Hide default radio/checkbox */
.fmd-root .fmd-form-check-input {
  position: absolute;
  opacity: 0;
}

/* Progress bar - thin and elegant */
.fmd-root .fmd-page-progress-container {
  height: 3px;
}

/* Subtle question descriptions */
.fmd-root .fmd-form-description {
  font-size: 16px;
  opacity: 0.7;
  margin-top: 8px;
}

/* Center everything vertically */
.fmd-root .fmd-slide {
  min-height: 70vh;
  display: flex;
  align-items: center;
}

/* Keyboard hint styling */
.fmd-root .fmd-btn::after {
  content: " ↵";
  opacity: 0.5;
  font-size: 0.8em;
}
```

## Recommended Settings

Use these `#!` settings for the most Typeform-like experience:

```markdown
#! rounded = pill
#! button-alignment = center
#! page-progress = show
#! slide-controls = hide
#! color-scheme = light
#! font-import-url = url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap')
#! font-family = 'Inter', system-ui, sans-serif
```

## Color Schemes

### Light (Default)
```markdown
#! background-color = #ffffff
#! color = #191919
#! accent = #0066ff
#! accent-foreground = #ffffff
```

### Dark
```markdown
#! color-scheme = dark
#! background-color = #1a1a2e
#! color = #eaeaea
#! accent = #6c63ff
#! accent-foreground = #ffffff
```

### Vibrant
```markdown
#! background-color = #6366f1
#! color = #ffffff
#! accent = #ffffff
#! accent-foreground = #6366f1
```

## Animation Enhancements (Optional)

For extra polish, add to the theme CSS:

```css
/* Fade-in animation for slides */
.fmd-root .fmd-slide-active {
  animation: typeform-slide-in 0.5s ease-out;
}

@keyframes typeform-slide-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Smooth focus transitions */
.fmd-root .fmd-form-field {
  transition: transform 0.3s ease;
}

.fmd-root .fmd-form-field:focus-within {
  transform: scale(1.01);
}
```
