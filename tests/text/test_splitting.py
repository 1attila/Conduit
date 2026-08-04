from mconduit.text.text import Text


def test_split_with_newlines():

    t1 = "Line1" * 1400
    t2 = "Line2" * 1300
    t3 = "Line3" * 400
    t = Text("\n".join([t1, t2, t3]))
    packets = t._split()
    
    assert len(packets) == 6
    assert packets[1].text == t1
    assert packets[3].text == t2
    assert packets[5].text == t3


def test_split_size_limit():

    large_text = "A" * 1500
    t = Text(large_text)
    packets = t._split()
        
    assert len(packets) > 1
        
    reconstructed = "".join(p.plain_text for p in packets)
    assert reconstructed == large_text