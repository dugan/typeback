#!/usr/bin/env python
from cStringIO import StringIO

text = """
python
print 2 + 3
print "2" + "3"
exit()
echo "You're still in the demo, but now you can type"
echo "Type exit to get back to your original shell."
"""

import typeback
typeback.typeback(StringIO(text))
