# Feature Dictionary

## Purpose
This document defines the meaning, type, role, and modeling relevance of the key variables used in the **Diamond Price Prediction and Market Segmentation** project.

It covers:
- raw dataset columns
- their analytical meaning
- expected data types
- their role in the project
- notes on preprocessing and interpretation
- candidate engineered features used later in the workflow

---

## Raw Feature Dictionary

| Feature | Type | Role | Description | Notes |
|---|---|---|---|---|
| carat | numeric | predictor | Weight of the diamond | Usually one of the strongest price drivers |
| cut | categorical | predictor | Quality of cut | Important quality indicator |
| color | categorical | predictor | Diamond color grade | Typically ordinal in domain meaning |
| clarity | categorical | predictor | Diamond clarity grade | Major quality and pricing factor |
| depth | numeric | predictor | Total depth percentage | Can influence pricing and geometry interpretation |
| table | numeric | predictor | Width of top relative to widest point | Useful proportion-related feature |
| price | numeric | target | Market price of the diamond | Target variable for regression |
| x | numeric | predictor | Length in millimeters | Used directly and for engineered geometry features |
| y | numeric | predictor | Width in millimeters | Used directly and for engineered geometry features |
| z | numeric | predictor | Depth in millimeters | Used directly and for engineered geometry features |

---

## Detailed Feature Definitions

## 1. `carat`

### Type
Numeric

### Role
Predictor

### Description
Represents the weight of the diamond.

### Why It Matters
Carat is usually the most influential raw variable in diamond pricing. Larger diamonds tend to be more expensive, but the relationship is rarely perfectly linear. Price often rises disproportionately as carat increases.

### Modeling Notes
- likely strongly predictive
- may be right-skewed
- may benefit from nonlinear treatment
- can support derived terms such as `carat_squared`

---

## 2. `cut`

### Type
Categorical

### Role
Predictor

### Description
Represents the quality of the cut.

### Common Categories
- Fair
- Good
- Very Good
- Premium
- Ideal

### Why It Matters
Cut quality influences visual appeal and perceived value. It can affect brilliance and customer desirability, which often influences price.

### Modeling Notes
- may be treated as nominal via one-hot encoding
- may also be treated as ordinal for clustering or special analysis
- should be validated against expected category values

---

## 3. `color`

### Type
Categorical

### Role
Predictor

### Description
Represents the color grade of the diamond.

### Common Categories
- D
- E
- F
- G
- H
- I
- J

### Why It Matters
Color is a major quality factor in diamond evaluation. Better color grades generally indicate higher quality.

### Modeling Notes
- domain ordering exists, but encoding choice depends on model design
- often handled with one-hot encoding in regression pipelines
- may be ordinal-encoded for clustering experiments

---

## 4. `clarity`

### Type
Categorical

### Role
Predictor

### Description
Represents the clarity grade of the diamond.

### Common Categories
- I1
- SI2
- SI1
- VS2
- VS1
- VVS2
- VVS1
- IF

### Why It Matters
Clarity reflects the visibility and extent of inclusions or imperfections. It is an important factor in price and perceived quality.

### Modeling Notes
- strongly relevant for price prediction
- often benefits from careful validation of category names
- may be encoded differently depending on the modeling path

---

## 5. `depth`

### Type
Numeric

### Role
Predictor

### Description
Represents total depth percentage.

### Why It Matters
Depth helps describe diamond proportions. Certain values may align more closely with preferred geometry and therefore affect pricing.

### Modeling Notes
- inspect for outliers or extreme values
- may participate in interaction features with `table`
- useful for both regression and clustering

---

## 6. `table`

### Type
Numeric

### Role
Predictor

### Description
Represents the width of the top facet relative to the widest point of the diamond.

### Why It Matters
Table is part of the proportional geometry of the diamond and may contribute to visual and pricing characteristics.

### Modeling Notes
- inspect distribution and outliers
- may interact with depth and dimensions
- often useful in proportional analysis

---

## 7. `price`

### Type
Numeric

### Role
Target

### Description
Represents the price of the diamond.

### Why It Matters
This is the main target variable for regression modeling.

### Modeling Notes
- expected to be positive
- often right-skewed
- may benefit from log transformation during modeling
- should not be used in target-derived engineered predictors for regression

### Segmentation Notes
Price may optionally be included in clustering if the goal is market-tier segmentation. If the goal is purely product-attribute clustering, price may be excluded.

---

## 8. `x`

### Type
Numeric

### Role
Predictor

### Description
Represents the length of the diamond in millimeters.

### Why It Matters
This provides direct geometric information and contributes to derived features such as estimated volume or aspect ratio.

### Modeling Notes
- validate suspicious zeros
- check range and outliers
- combine carefully with `y` and `z` for engineering

---

## 9. `y`

### Type
Numeric

### Role
Predictor

### Description
Represents the width of the diamond in millimeters.

### Why It Matters
Together with `x` and `z`, this helps characterize the physical proportions of the diamond.

### Modeling Notes
- validate zeros and implausible values
- may be highly related to `x`
- useful in derived geometric features

---

## 10. `z`

### Type
Numeric

### Role
Predictor

### Description
Represents the depth of the diamond in millimeters.

### Why It Matters
Provides dimensional depth beyond percentage-based `depth`, allowing more detailed geometric understanding.

### Modeling Notes
- validate suspicious zero values
- compare with `depth`
- useful for dimensional interactions and volume approximation

---

## Feature Grouping for Project Use

## Regression Predictors
These are the standard raw predictors for supervised modeling:
- carat
- cut
- color
- clarity
- depth
- table
- x
- y
- z

## Regression Target
- price

## Clustering Inputs
Potential clustering inputs may include:
- carat
- depth
- table
- x
- y
- z
- ordinal-encoded quality features
- optional price
- selected engineered geometric features

---

## Candidate Engineered Features

## 1. `volume_proxy`

### Formula
`x * y * z`

### Purpose
Acts as a rough proxy for geometric volume.

### Use
Helpful for modeling size-related variation beyond carat alone.

### Caution
This is not a physical certified volume measure; it is a practical derived approximation.

---

## 2. `length_width_ratio`

### Formula
`x / y`

### Purpose
Captures basic aspect ratio or shape proportion.

### Use
Can help detect proportion-related differences not obvious from raw dimensions alone.

### Caution
Requires safe handling if `y == 0`.

---

## 3. `depth_pct_from_dimensions`

### Example Logic
A derived proportion based on dimensional depth relative to planar dimensions.

### Purpose
Provides an alternate geometry-based view of depth.

### Use
Can complement or cross-check raw `depth`.

---

## 4. `table_depth_interaction`

### Formula
Combination or interaction of `table` and `depth`

### Purpose
Captures proportional interaction between two important geometry-related variables.

### Use
May help nonlinear models or linear models when explicit interactions are useful.

---

## 5. `carat_squared`

### Formula
`carat ** 2`

### Purpose
Allows simple nonlinear modeling of carat effect.

### Use
Often most useful for linear or regularized linear models.

---

## 6. `price_per_carat`

### Formula
`price / carat`

### Purpose
Descriptive and analytical feature for EDA.

### Use
Useful for studying pricing efficiency or relative pricing concentration.

### Critical Rule
This should **not** be used as a regression predictor because it is directly derived from the target.

---

## Validation Rules by Feature Type

### Numeric Validation
The following should be checked:
- non-negativity for numeric columns
- positive values where required
- suspicious zeros in dimension columns
- extreme outliers
- impossible ranges

### Categorical Validation
The following should be checked:
- allowed category membership
- spelling consistency
- unexpected or missing category values

---

## Expected Data Type Summary

| Feature | Expected Type |
|---|---|
| carat | float |
| cut | object / category |
| color | object / category |
| clarity | object / category |
| depth | float |
| table | float |
| price | int / float |
| x | float |
| y | float |
| z | float |

---

## Project Interpretation Notes

### Most Likely High-Impact Features
Likely high-impact predictors for price:
- carat
- clarity
- cut
- color
- geometry-related features

### Potentially Redundant Information
Potential overlap may exist among:
- carat
- x, y, z
- volume proxy
- depth-related measures

This does not necessarily require removal, but it does require thoughtful modeling and interpretation.

---

## Final Note
This feature dictionary is meant to support:
- data understanding
- preprocessing planning
- EDA interpretation
- model design
- clustering feature selection
- documentation quality

It should be updated if the dataset schema changes or if new engineered features become part of the official project pipeline.