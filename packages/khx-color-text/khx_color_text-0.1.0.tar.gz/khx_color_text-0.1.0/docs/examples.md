# **Examples**

Here are examples of all five supported colors with visual previews:

## Red
```python
cprint("Hello from khx_color_text in red!", "red")
```
<img src="assets/color_red.svg" alt="Red example" width="520">

## Green
```python
cprint("Hello from khx_color_text in green!", "green")
```
<img src="assets/color_green.svg" alt="Green example" width="520">

## Blue
```python
cprint("Hello from khx_color_text in blue!", "blue")
```
<img src="assets/color_blue.svg" alt="Blue example" width="520">

## Yellow
```python
cprint("Hello from khx_color_text in yellow!", "yellow")
```
<img src="assets/color_yellow.svg" alt="Yellow example" width="520">

## Cyan
```python
cprint("Hello from khx_color_text in cyan!", "cyan")
```
<img src="assets/color_cyan.svg" alt="Cyan example" width="520">

## Command Line Usage

You can also use the CLI tool:

```bash
khx-ct "Red text" --color red
khx-ct "Green text" --color green
khx-ct "Blue text" --color blue
khx-ct "Yellow text" --color yellow
khx-ct "Cyan text" --color cyan
```

## Error Handling

If you try to use an invalid color:

```python
cprint("This will fail", "purple")
# ValueError: Invalid color 'purple'. Allowed colors: blue, cyan, green, red, yellow
```