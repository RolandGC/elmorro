"""
ZPL (Zebra Programming Language) generator for thermal receipt printers.
Optimized for Zebra ZQ310 Plus printer with 58mm paper width.
"""

from decimal import Decimal
from typing import Optional


class ZPLGenerator:
    """
    Generate ZPL commands for Zebra thermal printers.
    Paper width: 58mm (approx 252 dots at 203dpi)
    """

    def __init__(self, width_mm: int = 58, dpi: int = 203):
        """
        Initialize ZPL generator.
        
        Args:
            width_mm: Paper width in millimeters (default 58mm)
            dpi: Printer resolution in dots per inch (default 203dpi)
        """
        self.width_mm = width_mm
        self.dpi = dpi
        self.width_dots = int(width_mm * dpi / 25.4)
        self.commands = []
        self.current_y = 20  # Starting Y position in dots

    def start_document(self):
        """Initialize ZPL document."""
        self.commands = []
        self.current_y = 20
        self.commands.append("^XA")  # Start ZPL
        self.commands.append("^LL500")  # Label length (height in dots)
        self.commands.append("^LS0")  # Label shift
        return self

    def add_line_spacing(self, height_dots: int = 15):
        """Add vertical spacing."""
        self.current_y += height_dots
        return self

    def add_text(
        self,
        text: str,
        x: int = 10,
        font_height: int = 40,
        font_width: int = 40,
        bold: bool = False,
        centered: bool = False,
    ):
        """
        Add text to label.
        
        Args:
            text: Text to print
            x: X position in dots (default 10)
            font_height: Font height in dots
            font_width: Font width in dots
            bold: Bold text (using thicker font)
            centered: Center text horizontally
        """
        if centered:
            x = (self.width_dots - len(text) * font_width // 2) // 2

        # ZPL font command: ^A (font) with options
        font_cmd = "^AF" if not bold else "^AB"
        self.commands.append(f"^FO{x},{self.current_y}")
        self.commands.append(f"{font_cmd}N,{font_height},{font_width}")
        self.commands.append(f"^FD{text}^FS")
        self.current_y += font_height + 5
        return self

    def add_title(self, text: str):
        """Add centered title."""
        self.add_line_spacing(10)
        self.add_text(text, font_height=50, font_width=50, bold=True, centered=True)
        self.add_line_spacing(5)
        return self

    def add_company_info(self, company_name: str, address: str, phone: str, mobile: str, website: str):
        """Add company header information."""
        self.add_title(company_name)
        self.add_text(address, x=10, font_height=24, font_width=20)
        self.add_text(f"Cel: {mobile}", x=10, font_height=24, font_width=20)
        # Phone line commented out as per HTML template
        self.add_text(f"Web: {website}", x=10, font_height=24, font_width=20)
        self.add_line_spacing(5)
        self.add_separator()
        return self

    def add_separator(self):
        """Add dotted separator line."""
        self.commands.append(f"^FO10,{self.current_y}")
        self.commands.append(f"^GB{self.width_dots - 20},2,2^FS")
        self.current_y += 10
        return self

    def add_receipt_header(self, series: str):
        """Add receipt number header."""
        self.add_text(f"Acuse de recibo: Serie {series}", x=10, font_height=28, font_width=24, centered=True)
        self.add_line_spacing(5)
        return self

    def add_sale_details(
        self,
        seller_name: str,
        client_name: str,
        client_dni: str,
        time_str: str,
        date_str: str,
        payment_condition: str,
        payment_method: Optional[str] = None,
        bank_name: Optional[str] = None,
        operation_number: Optional[str] = None,
        operation_date: Optional[str] = None,
        end_credit: Optional[str] = None,
    ):
        """Add sale details section."""
        self.add_text(f"Vendedor: {seller_name}", x=10, font_height=24, font_width=20)
        self.add_text(f"Cliente: {client_name}", x=10, font_height=24, font_width=20)
        self.add_text(f"DNI: {client_dni}", x=10, font_height=24, font_width=20)
        self.add_text(f"Hora: {time_str} del {date_str}", x=10, font_height=24, font_width=20)
        self.add_text(f"Pago: {payment_condition}", x=10, font_height=24, font_width=20)

        if payment_method:
            self.add_text(f"Metodo: {payment_method}", x=10, font_height=24, font_width=20)

        if bank_name:
            self.add_text(f"Banco: {bank_name}", x=10, font_height=24, font_width=20)

        if operation_number:
            self.add_text(f"Op: {operation_number}", x=10, font_height=24, font_width=20)

        if operation_date:
            self.add_text(f"F.Op: {operation_date}", x=10, font_height=24, font_width=20)

        if end_credit:
            self.add_text(f"Limite: {end_credit}", x=10, font_height=24, font_width=20)

        self.add_line_spacing(5)
        self.add_separator()
        return self

    def add_items_header(self):
        """Add items table header."""
        # Header row with columns: Cant. | Producto | P.Unid | Subtotal
        self.add_text("Cant.  Producto              P.Unid  Subtotal", x=10, font_height=22, font_width=18, bold=True)
        self.add_separator()
        return self

    def add_item(self, quantity: str, product_name: str, price: str, subtotal: str):
        """Add item row to table."""
        # Format: Qty | Product (truncated to fit) | Price | Subtotal
        product_short = product_name[:22] if len(product_name) > 22 else product_name.ljust(22)
        line = f"{quantity:>4}   {product_short:<22}  {price:>6}  {subtotal:>7}"
        self.add_text(line, x=10, font_height=20, font_width=18)
        return self

    def add_totals(
        self,
        subtotal: str,
        igv_percent: str,
        igv_amount: str,
        discount_percent: Optional[str] = None,
        discount_amount: Optional[str] = None,
        total: str = "",
    ):
        """Add totals section."""
        self.add_separator()
        self.add_text(f"Subtotal:          {subtotal}", x=10, font_height=24, font_width=20, bold=True)
        self.add_text(f"IGV {igv_percent}%:              {igv_amount}", x=10, font_height=24, font_width=20)

        if discount_percent and discount_amount:
            self.add_text(f"Descuento {discount_percent}%:        {discount_amount}", x=10, font_height=24, font_width=20)

        self.add_separator()
        self.add_text(f"TOTAL:             {total}", x=10, font_height=28, font_width=24, bold=True, centered=True)
        self.add_line_spacing(10)
        return self

    def add_comment(self, comment: str):
        """Add sale comment."""
        if comment and comment.strip():
            self.add_text(f"Comentario: {comment}", x=10, font_height=22, font_width=18)
            self.add_line_spacing(5)
        return self

    def add_payment_info(self, payment_condition: str, payment_method: Optional[str] = None, 
                        cash: Optional[str] = None, change: Optional[str] = None,
                        amount_debited: Optional[str] = None):
        """Add payment information message."""
        if payment_condition != 'contado':
            return self

        messages = []

        if payment_method == 'efectivoss':
            messages.append(f"Efectivo: {cash}")
            messages.append(f"Vuelto: {change}")
        elif payment_method == 'plinn':
            messages.append(f"Tarjeta: {amount_debited}")
        elif payment_method == 'efectivo_tarjeta':
            messages.append(f"Efectivo: {cash}")
            messages.append(f"Tarjeta: {amount_debited}")

        if messages:
            self.add_text("INFORMACION DE PAGO", x=10, font_height=24, font_width=20, centered=True)
            for msg in messages:
                self.add_text(msg, x=10, font_height=22, font_width=18, centered=True)
            self.add_line_spacing(5)

        return self

    def add_signatures(self):
        """Add signature lines."""
        self.add_text("___________         ___________", x=10, font_height=24, font_width=20, centered=True)
        self.add_text("Cliente         Vendedor", x=10, font_height=22, font_width=18, centered=True)
        self.add_line_spacing(5)
        return self

    def add_footer(self):
        """Add footer message."""
        self.add_separator()
        self.add_text("!Gracias por su preferencia!", x=10, font_height=26, font_width=22, centered=True)
        self.add_text("Brindando atencion eficiente", x=10, font_height=22, font_width=18, centered=True)
        self.add_text("de calidad", x=10, font_height=22, font_width=18, centered=True)
        self.add_line_spacing(20)
        return self

    def end_document(self):
        """Finalize ZPL document."""
        self.commands.append("^XZ")  # End ZPL
        return self

    def get_zpl(self) -> str:
        """Get generated ZPL string."""
        return "\n".join(self.commands)

    @staticmethod
    def generate_from_sale(sale, company):
        """
        Generate ZPL from Sale object.
        
        Args:
            sale: Sale model instance
            company: Company model instance
            
        Returns:
            str: ZPL command string
        """
        from django.utils import timezone
        from django.utils.timezone import localtime

        zpl = ZPLGenerator()
        zpl.start_document()

        # Company header
        zpl.add_company_info(
            company_name=company.name,
            address=company.address or "",
            phone=company.phone or "",
            mobile=company.mobile or "",
            website=company.website or "",
        )

        # Receipt header
        zpl.add_receipt_header(str(sale.serie))

        # Sale details
        date_joined = localtime(sale.date_joined) if sale.date_joined else None
        time_str = date_joined.strftime("%H:%M") if date_joined else "-"
        date_str = date_joined.strftime("%d/%m/%Y") if date_joined else "-"

        zpl.add_sale_details(
            seller_name=sale.employee.full_name if sale.employee else "",
            client_name=sale.client.user.full_name if sale.client else "",
            client_dni=sale.client.user.dni if sale.client else "",
            time_str=time_str,
            date_str=date_str,
            payment_condition=sale.get_payment_condition_display(),
            payment_method=sale.get_payment_method_display() if sale.payment_condition == 'contado' else None,
            bank_name=sale.payment_bank.name if hasattr(sale, 'payment_bank') and sale.payment_bank else None,
            operation_number=sale.operation_number if sale.operation_number else None,
            operation_date=str(sale.operation_date) if sale.operation_date else None,
            end_credit=str(sale.end_credit) if sale.end_credit else None,
        )

        # Items
        zpl.add_items_header()
        for detail in sale.saledetail_set.all():
            zpl.add_item(
                quantity=str(int(detail.cant)),
                product_name=detail.product.name,
                price=f"{detail.price:.2f}",
                subtotal=f"{detail.total:.2f}",
            )

        # Totals
        zpl.add_totals(
            subtotal=f"{sale.subtotal:.2f}",
            igv_percent=str(int(sale.igv)),
            igv_amount=f"{sale.total_igv:.2f}",
            discount_percent=str(int(sale.dscto)) if sale.dscto > 0 else None,
            discount_amount=f"{sale.total_dscto:.2f}" if sale.dscto > 0 else None,
            total=f"{sale.total:.2f}",
        )

        # Comment
        if sale.comment:
            zpl.add_comment(sale.comment)

        # Payment info
        zpl.add_payment_info(
            payment_condition=sale.payment_condition,
            payment_method=sale.payment_method if sale.payment_condition == 'contado' else None,
            cash=f"{sale.cash:.2f}" if sale.payment_method == 'efectivoss' else None,
            change=f"{sale.change:.2f}" if sale.payment_method == 'efectivoss' else None,
            amount_debited=f"{sale.amount_debited:.2f}" if sale.amount_debited else None,
        )

        # Signatures
        zpl.add_signatures()

        # Footer
        zpl.add_footer()

        # Finalize
        zpl.end_document()

        return zpl.get_zpl()
