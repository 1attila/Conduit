from mconduit import text


t = text.Table("Title", columns=3, mode=text.DisplayMode.Horizontal)

t.insert(text.Text("-A-"), text.Text("1"), text.Text("1"))
t.insert("-B", "2", "B2")

""" t.insert("-A-", "-B")
t.insert("1", "2")
t.insert("1", "B2") """

# print(t.data)

for l in t.draw():
    print(l)

for l in t.draw(alignment=text.Alignment.Left, draw_rows=False):
    print(l)

for l in t.draw(alignment=text.Alignment.Right, draw_columns=False):
    print(l)

for l in t.draw(draw_columns=False, draw_rows=False):
    print(l)