from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 10)
        self.cell(0, 10, get_display(arabic_reshaper.reshape('صفحة %s' % self.page_no())), 0, 0, 'C')

pdf = PDF()
pdf.add_page()

pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)

text = """
وكالة عامة

أنا الموقع أسفله:
الاسم واللقب: الورغي منير
مكان الإقامة: إيطاليا
رقم الهوية الوطنية: ................................

أفوّض بموجب هذه الوكالة والدتي،
الاسم واللقب: أصفية العسري
مكان الإقامة: ................................

بكل صلاحيات التصرف نيابة عني، للقيام بكافة الإجراءات والمباشرة بكل الأعمال المتعلقة بالأوراق الإدارية والرسمية، والمرفقات، وكافة المعاملات المتعلقة بالبقعة العقارية التي أمتلكها في بحيرة فاس، وذلك من أجل بناء منزل فيها.

تشمل هذه الوكالة الحق في توقيع الوثائق، استلام الشواهد، تقديم الطلبات، التوقيع على العقود، التواصل مع الإدارات المختصة، وكل ما يلزم لإنجاز هذه المعاملات.

وقد منحت هذه الوكالة من طرفي كاملة الصلاحية القانونية، وتظل سارية المفعول حتى إشعار آخر مني.

حررت هذه الوكالة بمدينة ........................، بتاريخ ........................
رقم البقعة: ................................

التوقيع:
الورغي منير
"""

# Reshape et bidi sur tout le texte d'un coup
reshaped_text = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped_text)

pdf.multi_cell(0, 10, bidi_text, align='R')

pdf.output("procuration_correcte.pdf")
print("PDF généré avec texte arabe correctement ordonné et formaté.")
