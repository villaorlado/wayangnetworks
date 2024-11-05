# The networks of Wayang Kulit

This is a project by [Miguel Escobar](http://miguelescobar.com) and [Andy Schauf](https://github.com/AndySchauf). It xplores how the stories of _Wayang Kulit_ through network visualization and analysis.

See the [interactive version](https://villaorlado.github.io/wayangnetworks/html/). Clicking on the characters displays information about the network measurements and history of each character. This information is also linked to annotated summaries of 24 famous wayang stories.

## Research ouput

Two papers detailing this work are available here:

Escobar Varela, M. (2019) [Towards a digital, data-driven wayang kulit encyclopedia](https://www.tandfonline.com/doi/abs/10.1080/13639811.2019.1553382), Indonesia and the Malay World, DOI: 10.1080/13639811.2019.1553382

Schauf, A., & Escobar Varela, M. (2018). [Searching for hidden bridges in co-occurrence networks from Javanese wayang kulit](https://jhnr.uni.lu/index.php/jhnr/article/view/42). Journal of Historical Network Research, 2(1), 26-52. https://doi.org/10.25517/jhnr.v2i1.42

## Repository Structure

### 1. Texts (`1_texts/`)
Original source materials - the raw text files containing the stories for analysis.

### 2. Network data (`2_network_data/`)
Processed datasets for:
- Network analysis
- Simulations
- Null model comparisons

### 3. Experiments (`3_experiments/`)
*(previously 5_experiments)*
Python scripts for:
- Network analysis
- Simulations
- Null model comparisons

### 4. Network Visualization (`4_network_visualization/`)
*(previously 6_gephi)*
Gephi files for network visualization.

### 5. Web Content (`5_web_content/`)
*(previously 2_data_for_static_site)*
Structured data prepared for the website:
- Character information
- Relationship data
- Metadata

### 6. Site Generator (`6_site_generator/`)
Tools to generate the static website:
- Templates
- Build scripts
- Asset processing

### Output (`html/`)
The final built website with all visualizations and analysis.