# Medication Types Guide

PAAS National supports comprehensive processing across 8 major medication categories, each with specialized calculation logic.

## 1. Nasal Inhalers

**Database**: 33+ products  
**Examples**: Flonase, Nasacort, Beconase AQ, Dymista

### Key Features
- **Spray Count Validation**: Tracks total sprays per package
- **Package Size Calculations**: Determines optimal package quantities
- **Seasonal vs Maintenance**: Handles different dosing patterns

### Calculation Logic
- Uses total sprays per package from database
- Calculates daily spray usage from sig
- Determines day supply: `total_sprays / daily_usage`
- Bounds result between 7-365 days

### Example
```python
# Flonase 50mcg: 120 sprays per bottle
# Sig: "2 sprays each nostril daily" = 4 sprays/day
# Day supply: 120 / 4 = 30 days
```

## 2. Oral Inhalers

**Database**: 40+ products  
**Examples**: Albuterol HFA, Ventolin, Advair, Symbicort

### Key Features
- **Puff Tracking**: Monitors total puffs per inhaler
- **Discard Date Enforcement**: Applies beyond-use date limits
- **Rescue vs Maintenance**: Differentiates inhaler types

### Calculation Logic
- Uses total puffs per inhaler from database
- Calculates daily puff usage from sig
- Applies discard date limits (typically 90 days)
- Final day supply: `min(calculated_days, discard_limit)`

### Example
```python
# Albuterol HFA: 200 puffs per inhaler
# Sig: "2 puffs q4h prn" = ~12 puffs/day
# Calculated: 200 / 12 = 16.7 days
# With 90-day discard limit: 16 days
```

## 3. Insulin Products

**Database**: 56+ products  
**Examples**: Humalog, Lantus, NovoLog, Tresiba

### Key Features
- **Unit Calculations**: Precise insulin unit tracking
- **Beyond-Use Date Limits**: Enforces expiration after opening
- **Pen vs Vial Handling**: Different calculations for each form
- **Sliding Scale Support**: Handles variable dosing

### Calculation Logic
- Uses total units per package from database
- Calculates daily unit usage from sig
- Applies 28-day beyond-use date for most insulins
- Special handling for U-500 and concentrated insulins

### Example
```python
# Humalog KwikPen: 300 units per pen
# Sig: "15 units before meals TID" = 45 units/day
# Calculated: 300 / 45 = 6.7 days per pen
# For 5 pens: 5 × 6.7 = 33 days (within 28-day limit)
```

## 4. Injectable Biologics

**Database**: 43+ products  
**Examples**: Humira, Enbrel, Stelara, Cosentyx

### Key Features
- **Complex Dosing Schedules**: Weekly, biweekly, monthly patterns
- **Strength Calculations**: Handles various concentrations
- **Loading Doses**: Accounts for initial higher doses

### Calculation Logic
- Uses package strength and volume from database
- Calculates dose frequency from sig
- Handles complex schedules (e.g., "weekly for 4 weeks, then monthly")
- Applies appropriate day supply calculations

### Example
```python
# Humira 40mg/0.8mL pen
# Sig: "40mg subcutaneously every other week"
# Frequency: 14 days between doses
# For 2 pens: 2 × 14 = 28 days
```

## 5. Injectable Non-Biologics

**Database**: 42+ products  
**Examples**: Testosterone, B12, EpiPen, Depo-Provera

### Key Features
- **Varied Administration Routes**: IM, SubQ, IV
- **Multiple Frequencies**: Daily, weekly, monthly, PRN
- **Emergency Medications**: Special handling for EpiPens, etc.

### Calculation Logic
- Uses volume and concentration from database
- Calculates injection frequency from sig
- Handles PRN medications with estimated usage
- Special logic for emergency medications

### Example
```python
# Testosterone Cypionate 200mg/mL, 10mL vial
# Sig: "200mg IM every 2 weeks"
# Doses per vial: 10 doses
# Day supply: 10 × 14 = 140 days
```

## 6. Eye Drops

**Database**: Comprehensive PBM coverage  
**Examples**: Timolol, Latanoprost, Restasis, Lumigan

### Key Features
- **PBM-Specific Calculations**: Different drops/mL by insurance
- **Beyond-Use Dates**: Enforces discard dates after opening
- **Solution vs Suspension**: Different drop counts

### PBM Guidelines
- **Caremark**: 16 drops/mL (solution), 12 drops/mL (suspension)
- **Express Scripts**: 20 drops/mL (solution), 15 drops/mL (suspension)
- **Humana**: 18 drops/mL (solution), 14 drops/mL (suspension)
- **OptumRx**: 20 drops/mL (solution), 16 drops/mL (suspension)

### Example
```python
# Timolol 0.5% 5mL bottle
# Sig: "1 drop each eye BID" = 4 drops/day
# Using Caremark: 5mL × 16 drops/mL = 80 drops
# Day supply: 80 / 4 = 20 days
```

## 7. Topical Medications

**Database**: FTU-based dosing guide  
**Examples**: Hydrocortisone, Betamethasone, Clobetasol

### Key Features
- **Fingertip Unit (FTU) Calculations**: Body area-specific dosing
- **Potency-Based Guidelines**: Different amounts by steroid class
- **Application Frequency**: BID, TID, QID support

### FTU Dosing by Body Area
- **Face/Neck**: 2.5g per application
- **Hand**: 1.0g per application
- **Arm**: 3.0g per application
- **Leg**: 6.0g per application
- **Trunk**: 14.0g per application

### Example
```python
# Hydrocortisone 1% cream, 30g tube
# Sig: "Apply to affected area on arms BID"
# FTU for arms: 3.0g × 2 applications = 6g/day
# Day supply: 30g / 6g = 5 days
```

## 8. Diabetic Injectables

**Database**: 25+ products  
**Examples**: Ozempic, Trulicity, Mounjaro, Victoza

### Key Features
- **Pen-Specific Dosing**: Each pen has specific dose increments
- **Titration Schedules**: Handles dose escalation protocols
- **GLP-1 Combinations**: Special handling for combination therapies

### Dosing Increments
- **Ozempic**: 0.25mg, 0.5mg, 1mg, 2mg
- **Trulicity**: 0.75mg, 1.5mg, 3mg, 4.5mg
- **Mounjaro**: 2.5mg, 5mg, 7.5mg, 10mg, 12.5mg, 15mg

### Example
```python
# Ozempic 2mg/1.5mL pen (4 doses of 0.5mg each)
# Sig: "0.5mg subcutaneously weekly"
# Doses per pen: 4
# Day supply: 4 × 7 = 28 days
```

## Pattern Recognition

For medications not in the database, PAAS National uses intelligent pattern recognition:

### Drug Name Patterns
- **Insulin keywords**: "insulin", "lantus", "humalog", "novolog"
- **Inhaler keywords**: "hfa", "inhaler", "albuterol", "advair"
- **Eye drop keywords**: "drops", "ophth", "eye", "timolol"
- **Topical keywords**: "cream", "ointment", "gel", "lotion"

### Sig Pattern Recognition
- **Frequency terms**: "daily", "BID", "TID", "QID", "q4h", "prn"
- **Route indicators**: "inject", "inhale", "apply", "instill"
- **Quantity terms**: "units", "puffs", "sprays", "drops", "mg"

## Quality Assurance

All medication types undergo rigorous testing:

- **100% Database Coverage**: Every drug tested individually
- **Edge Case Handling**: Unusual quantities and dosing patterns
- **Real-World Validation**: Based on actual pharmacy data
- **Continuous Updates**: Database maintained with new products

## Integration Notes

When integrating PAAS National:

1. **Medication Type Access**: Use `result.medication_type.value`
2. **Additional Info**: Check `result.additional_info` for type-specific data
3. **Confidence Scores**: Monitor `result.confidence_score` for match quality
4. **Batch Processing**: Use `batch_process()` for multiple prescriptions
