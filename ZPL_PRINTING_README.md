# Impresión de Tickets - PDF y ZPL para Zebra ZQ310 Plus

## Descripción

Este módulo proporciona soporte para imprimir tickets en dos formatos:
- **PDF**: Vista previa y impresión estándar en navegador
- **ZPL**: Formato optimizado para impresoras térmicas Zebra

## Características

- ✅ Previsualización en HTML en el navegador
- ✅ Impresión en PDF (navegador)
- ✅ Generación de comandos ZPL para Zebra ZQ310 Plus
- ✅ Auto-detección de dispositivos Android
- ✅ Control de formato mediante parámetro `format` en URL

## Uso

### 1. Desde el navegador (PDF)

URL predeterminada (formato PDF):
```
/pos/crm/sale/print/voucher/{id}/
/pos/crm/sale/print/voucher/{id}/?format=pdf
```

### 2. Para impresora Zebra (ZPL)

URL con formato ZPL:
```
/pos/crm/sale/print/voucher/{id}/?format=zpl
```

### 3. Desde JavaScript (Auto-detección en Android)

```javascript
// Auto-detecta Android y usa ZPL, sino usa PDF
printTicket(saleId);

// Fuerza PDF
printTicketPDF(saleId);

// Fuerza ZPL
printTicketZPL(saleId);
```

## Integración en plantillas HTML

### Agregar el script en tu plantilla:

```html
<script src="{% static 'crm/sale/print/print_manager.js' %}"></script>
```

### Botón que auto-detecta formato:

```html
<button onclick="printTicket({{ sale.id }})" class="btn btn-primary">
    <i class="fas fa-print"></i> Imprimir
</button>
```

### Botones específicos:

```html
<a href="/pos/crm/sale/print/voucher/{{ sale.id }}/" target="_blank" class="btn btn-primary">
    <i class="fas fa-file-pdf"></i> PDF
</a>

<button onclick="printTicketZPL({{ sale.id }})" class="btn btn-info">
    <i class="fas fa-print"></i> ZPL
</button>
```

## Configuración de la impresora Zebra ZQ310 Plus

### Requisitos:
- Impresora Zebra ZQ310 Plus
- Ancho de papel: 58mm
- Resolución: 203 dpi

### Configuración en Android:

1. **Instalar aplicación Zebra SetupUtilities** (opcional, para configuración)
2. **Instalar Zebra Link-OS SDK** o compatible
3. **Conectar impresora**:
   - USB (recomendado)
   - Bluetooth
   - WiFi

### Envío de comandos ZPL desde Android:

#### Opción 1: Usar Zebra Mobile Print App
```
- Copiar contenido ZPL
- Abrir Zebra Mobile Print
- Seleccionar impresora
- Pegar comando ZPL
- Imprimir
```

#### Opción 2: Integración programática (Android Java)
```java
// Con Zebra Link-OS SDK
Connection connection = new UsbConnection();
connection.open();
ZebraPrinter printer = ZebraPrinterFactory.getInstance(connection);
String zplCommand = /* comando ZPL */;
printer.sendCommand(zplCommand);
connection.close();
```

#### Opción 3: Envío HTTP a impresora en red
```javascript
// Si la impresora está configurada con IP
fetch('http://{printer-ip}:9100/pstatus', {
    method: 'POST',
    body: zplContent
});
```

## Características ZPL Implementadas

### Especificaciones técnicas:
- **Ancho máximo**: 58mm (252 puntos a 203 dpi)
- **Altura automática**: Se ajusta al contenido
- **Fuentes**: ZPL predeterminadas (A, B)
- **Códigos de barras**: Listo para expansión

### Elementos incluidos:
✅ Logo de empresa (no incluido en ZPL, requiere configuración en impresora)
✅ Nombre y datos de la empresa
✅ Información de venta (cliente, vendedor, fecha, hora)
✅ Tabla de productos con cantidad, precio, subtotal
✅ Cálculos (subtotal, IGV, descuento, total)
✅ Información de pago (método, referencia de operación)
✅ Líneas de firma
✅ Mensaje de agradecimiento

## Solución del problema original

### Problema:
Al imprimir PDF, hay demasiado espacio en blanco al final

### Solución con ZPL:
1. **Altura dinámica**: ZPL genera comandos con altura exacta necesaria
2. **Sin espacios en blanco**: Se ajusta perfectamente al contenido
3. **Corte automático**: La impresora Zebra ZQ310 Plus soporta corte automático
4. **Mejor control**: Control total sobre cada píxel

## Archivos modificados

```
core/pos/
├── utils/
│   └── zpl_generator.py          # Nuevo: Generador ZPL
├── views/
│   └── crm/sale/print/
│       └── views.py              # Modificado: Soporte ZPL
└── static/
    └── crm/sale/print/
        └── print_manager.js      # Nuevo: Manager de impresión
```

## Ejemplo de comando ZPL generado

```zpl
^XA
^LL500
^LS0
^FO10,20
^AB N,50,50
^FDCOMPANY NAME^FS
^FO10,75
^AF N,24,20
^FDAddress^FS
... (más contenido)
^XZ
```

## Testing

### Test de ZPL:
1. Acceder a: `/pos/crm/sale/print/voucher/{id}/?format=zpl`
2. Copiar contenido del navegador
3. Probar en simulador Zebra o impresora física

### Test de PDF:
1. Acceder a: `/pos/crm/sale/print/voucher/{id}/`
2. Debe abrirse previsualizador PDF en navegador

## Futuras mejoras

- [ ] Integración de códigos QR en ZPL
- [ ] Códigos de barras EAN13
- [ ] Imágenes de logo codificadas en ZPL
- [ ] Descarga automática en Android
- [ ] Integración con Zebra Mobile Services API
- [ ] Configuración por sucursal de tipo de impresora

## Soporte

Para problemas con ZPL, consulta:
- [Zebra ZPL Programming Guide](https://www.zebra.com/content/dam/zebra_new/en_us/software/zpl-command-reference_1.pdf)
- [ZQ310 Plus Datasheet](https://www.zebra.com/us/en/products/printers/mobile/zq310-mobile-label-printer.html)
- Documentación de Zebra Link-OS SDK
