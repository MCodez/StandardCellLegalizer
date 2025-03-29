# **Standard Cell Legalizer**  

## **Overview**  
Standard cell legalization is a critical step in **VLSI physical design**, ensuring that cells are placed without overlaps while adhering to design rules. This algorithm efficiently resolves **cell overlaps** and aligns them to a grid while keeping movement minimal.  

## **Features**  
- ✔ **Grid-based snapping** – Aligns cells to predefined grid points for structured placement.  
- ✔ **Overlap detection and resolution** – Handles **cell-to-cell** and **boundary overlaps** efficiently.  
- ✔ **Minimal displacement strategy** – Moves cells in the **least movement direction** to minimize disruptions.  
- ✔ **Deadlock handling** – Avoids infinite loops due to conflicting moves.  
- ✔ **Visual comparison** – Generates **before-and-after plots** of cell placement.  
- ✔ **Summary report** – Provides details on movement per cell and the **maximum movement required**.  

## **Applications**  
📌 **VLSI Physical Design** – Ensures proper **standard cell legalization** in chip layout.  
📌 **EDA Tool Development** – Can be integrated into **place-and-route (PnR) tools**.  
📌 **Computational Geometry** – Useful for **polygon placement** and **overlap resolution** in general applications.  

## **Algorithm Workflow**  
1. **Snap cells to grid** based on the predefined **grid height**.  
2. **Filter out cells** that are **outside the block boundary** (ignored in further processing).  
3. **Detect overlaps** with **other cells** and the **block boundary**.  
4. **Compute displacement vectors** for each overlapping cell in all four directions (**left, right, up, down**).  
5. **Move the cell in the direction requiring the least displacement** while maintaining alignment to the grid.  
6. **Update cell positions** dynamically to avoid **conflicting movements**.  
7. **Handle deadlocks** by restoring the original position if movement oscillates.  
8. **Visualize results** by plotting **initial and final cell locations**.  
9. **Summarize movements**, identifying:  
   - Movement per cell  
   - **Maximum movement required**  
   - **Which cell moved the most**  

## **How to Run**  

### 1️⃣ Clone the Repository  
```sh
git clone https://github.com/yourusername/StandardCellLegalizer.git
```

### 2️⃣ Run the code
```
python standardcelllegalization.py
```

## Output Visualization

Below is the generated visualization from the algorithm:

![Visualization](cell_placement_plot.png?)
