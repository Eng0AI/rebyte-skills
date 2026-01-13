# Forms.md DSL Syntax Reference

## Settings (Top of File)

```markdown
#! title = My Survey
#! post-url = /api/submit
#! accent = #6366f1
#! color-scheme = light
#! localization = en
#! page = form-slides
```

| Setting | Values | Description |
|---------|--------|-------------|
| `title` | string | Page title |
| `post-url` | URL | Form submission endpoint |
| `accent` | hex/rgb/name | Primary color |
| `accent-foreground` | hex/rgb/name | Text on accent background |
| `background-color` | hex/rgb/name | Page background |
| `color` | hex/rgb/name | Text color |
| `color-scheme` | `light`/`dark` | Default theme |
| `localization` | `en`/`es`/`fr`/`de`/`ja`/`zh`/`ar`/`bn`/`pt` | Language |
| `page` | `form-slides`/`slides`/`single` | Layout mode |
| `rounded` | `none`/`pill` | Button/input rounding |
| `font-family` | CSS font stack | Custom font |
| `font-import-url` | URL | Google Fonts import |

## Slide Controls

```markdown
---                          # New slide separator
-> condition                 # Logic jump (show if true)
-> start                     # Start slide
-> start -> Let's begin!     # Start slide with custom button
-> end                       # End slide
-> end -> https://example.com  # End slide with redirect
|> 50%                       # Progress indicator
|> 2/5                       # Progress as fraction
=| center                    # Button alignment: start/center/end/stretch
<< disable                   # Disable back button
>> post                      # Submit data at this slide
```

## Form Fields

### Syntax Pattern
```
fieldName* = FieldType(
    | question = Your question here
    | description = Optional help text
    | placeholder = Placeholder text
    | fieldSize = sm
    | labelStyle = classic
)
```

`*` after name = required field. `|` is parameter delimiter.

### Field Types

**TextInput**
```
name* = TextInput(
    | question = What's your name?
    | placeholder = John Doe
    | multiline
    | maxlength = 100
    | pattern = [A-Za-z]+
    | value = Default
)
```

**EmailInput**
```
email* = EmailInput(
    | question = Your email?
    | placeholder = you@example.com
)
```

**NumberInput**
```
age = NumberInput(
    | question = Your age?
    | min = 18
    | max = 100
    | step = 1
    | unit = $
    | unitEnd = USD
)
```

**ChoiceInput** (radio/checkbox)
```
role* = ChoiceInput(
    | question = Your role?
    | choices = Developer, Designer, Manager, Other
    | multiple
    | horizontal
    | checked = Developer
)
```

**SelectBox**
```
country = SelectBox(
    | question = Country?
    | placeholder = Select one
    | options = USA, Canada, UK, Germany
    | selected = USA
)
```

**RatingInput**
```
rating* = RatingInput(
    | question = How would you rate us?
    | outof = 5
    | icon = star
)
```

**OpinionScale**
```
nps = OpinionScale(
    | question = How likely to recommend?
    | startAt = 0
    | outof = 10
    | labelStart = Not likely
    | labelEnd = Very likely
)
```

**DateInput / TimeInput / DatetimeInput**
```
birthday = DateInput(
    | question = Birthday?
    | min = 1900-01-01
    | max = 2024-12-31
)
```

**FileInput**
```
resume = FileInput(
    | question = Upload resume
    | sizeLimit = 10
    | imageOnly
)
```

**TelInput**
```
phone = TelInput(
    | question = Phone number?
    | country = US
    | availableCountries = US, CA, UK
)
```

**PictureChoice**
```
pet = PictureChoice(
    | question = Pick your favorite
    | choices = Dog && https://img.com/dog.jpg, Cat && https://img.com/cat.jpg
    | multiple
    | supersize
    | hideLabels
)
```

## Conditional Logic

### Logic Jumps (Skip slides)
```markdown
---
-> age >= 18
# Adult Questions
...

---
-> age < 18
# Minor Questions
...
```

### Conditional Display (Within slide)
```markdown
::: [{$ fieldName $}]
{% if fieldName == "Other" %}
otherField = TextInput(| question = Please specify)
{% endif %}
:::
```

## Content Elements

Standard Markdown works: `# Heading`, `**bold**`, `*italic*`, `[link](url)`, `![image](url)`, lists, code blocks.

### Custom Div with Data Binding
```markdown
::: [.my-class {$ name email $}]
Hello {{ name }}, we'll contact you at {{ email }}.
:::
```
