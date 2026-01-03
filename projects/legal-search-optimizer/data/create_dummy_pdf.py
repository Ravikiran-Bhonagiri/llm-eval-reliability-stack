from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 800, "SUPREME COURT OF THE UNITED STATES")
    c.drawString(100, 780, "Syllabus")
    c.drawString(100, 760, "GOOGLE LLC v. ORACLE AMERICA, INC.")
    
    text = """
    Held: Google's copying of the Java SE API, which included only those 
    lines of code that were needed to allow programmers to put their accrued 
    talents to work in a new and transformative program, was a fair use of 
    that material as a matter of law.
    
    ... (simulating 50 pages of legal text) ...
    
    The Copyright Act's fair use provision, 17 U. S. C. §107, observes that 
    "fair use of a copyrighted work . . . is not an infringement of copyright."
    """
    
    y = 740
    for line in text.split('\n'):
        c.drawString(100, y, line.strip())
        y -= 20
        
    c.save()

if __name__ == "__main__":
    create_pdf("data/landmark_cases.pdf")
