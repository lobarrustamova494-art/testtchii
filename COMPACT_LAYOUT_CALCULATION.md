# Compact Layout Hisoblash

## A4 Sahifa O'lchamlari

- Umumiy balandlik: 297mm
- Footer boshlanishi: 275mm
- Mavjud balandlik: 275mm

## Grid Boshlanishi

- Header: 15 + 28 = 43mm
- Student Info: 43 + 84 = 127mm
- Instructions: 127 + 22 = 149mm
- **Grid Start: 149mm**

## Mavjud Joy

275mm (footer) - 149mm (grid start) = **126mm**

## Compact Layout (Yangi)

### Bitta Mavzu + Bo'lim uchun:

- Topic header: 6mm (kamaytirildi 8mm dan)
- Topic spacing: 8mm (kamaytirildi 10mm dan)
- Section header: 5mm (kamaytirildi 6mm dan)
- **Jami overhead: 19mm**

### Savollar uchun:

- Row height: 5mm (kamaytirildi 6mm dan)
- Section orasida: 2mm (kamaytirildi 3mm dan)
- Topic orasida: 3mm (kamaytirildi 5mm dan)

## 80 Ta Savol uchun Hisoblash

### Variant 1: Bitta Mavzu, Bitta Bo'lim

```
Overhead: 19mm
Savollar: 80 / 2 = 40 qator
Qatorlar: 40 × 5mm = 200mm
Jami: 19 + 200 = 219mm ✅ SIG'ADI! (126mm dan kam emas, lekin...)
```

Xato! 219mm > 126mm. Sig'maydi!

### Variant 2: Ikki Mavzu

```
Mavzu 1: 19mm + (20 qator × 5mm) = 119mm
Mavzu 2: 3mm (spacing) + 19mm + (20 qator × 5mm) = 122mm
Jami: 119 + 122 = 241mm ❌ SIG'MAYDI!
```

### Variant 3: To'rtta Mavzu (har birida 20 ta savol)

```
Mavzu 1: 19mm + (10 qator × 5mm) = 69mm
Mavzu 2: 3mm + 19mm + (10 qator × 5mm) = 72mm
Mavzu 3: 3mm + 19mm + (10 qator × 5mm) = 72mm
Mavzu 4: 3mm + 19mm + (10 qator × 5mm) = 72mm
Jami: 69 + 72 + 72 + 72 = 285mm ❌ SIG'MAYDI!
```

## Muammo

80 ta savolni bitta sahifaga sig'dirish **MUMKIN EMAS** hozirgi layout bilan!

## Yechimlar

### Yechim 1: Header/Student Info'ni Kamaytirish

- Student ID grid'ni olib tashlash: -48mm
- Yangi mavjud joy: 126 + 48 = 174mm
- 80 savol uchun kerak: ~220mm
- Hali ham yetmaydi!

### Yechim 2: Ikki Ustun (4 savol bir qatorda)

- 80 savol / 4 = 20 qator
- 20 × 5mm = 100mm
- Overhead: ~20mm
- Jami: 120mm ✅ SIG'ADI!

### Yechim 3: Kichikroq Font va Spacing

- Row height: 4mm (5mm dan)
- 40 qator × 4mm = 160mm
- Overhead: 20mm
- Jami: 180mm
- Hali ham ko'p!

## Tavsiya

**Eng yaxshi yechim:** Ikki ustun (4 savol bir qatorda)

Afzalliklari:

- 80 ta savol sig'adi
- O'qish oson
- OMR detection oson

Kamchiliklari:

- Doirachalar kichikroq bo'ladi
- Horizontal spacing kam

## Hozirgi Holat

Compact layout bilan:

- **~60-65 ta savol** sig'adi bitta sahifaga
- 80 ta savol uchun 2 sahifa kerak
- Yoki layout'ni yanada optimallashtirishimiz kerak
