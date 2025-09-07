'''This file was generated automatically by `r_pythonize.py`.
It converts R modules into a pandas series,
ready to be called by rpy2.robjects.r() method.
Author of R code:
Gabriel Martinez [gabriel.martinez@cinvestav.mx]
Andres Tinajero [jesus.tinajero@cinvestav.mx]'''

from pandas import Series
modules= dict()
modules['Module_1']= '''
########################################
# Module 1 | Install and load packages #
########################################


## Step 0: Load and install required packages.


# Function to check and install packages from CRAN and Bioconductor
check_and_install_packages <- function(packages) {
  # Initialize lists to store installation and loading results
  loaded_successfully <- c()
  failed_to_load <- c()

  # Load the installed packages
  lapply(packages, function(pkg) {
    if (require(pkg, character.only = TRUE)) {
      loaded_successfully <<- c(loaded_successfully, pkg)
    } else {
      failed_to_load <<- c(failed_to_load, pkg)
    }
  })

  # Display a summary of installation and loading results
  message("\n--- Package Installation and Loading Summary ---")
  if (length(loaded_successfully) > 0) {
    message("Successfully loaded packages: ", paste(loaded_successfully, collapse = ", "))
  }
  if (length(failed_to_load) > 0) {
    stop("Packages that failed to load: ", paste(failed_to_load, collapse = ", "))
  }
}

# List of required packages
required_packages <- c("ggtree", "tidytree", "ggplot2", "dplyr", "tidyr",
                       "RColorBrewer", "gridExtra", "cowplot", "treeio",
                       "ggtreeExtra", "phangorn", "grid", "magick", "here",
                       "ggimage", "svglite")

# Check and install the required packages
check_and_install_packages(required_packages)

'''

modules['Module_2']='''
#######################################
# Module 2 | Read, load and plot tree #
#######################################

# This script will be called by the python program revolutionhtl.plot_summary
# The variables bellow are suposed to be created by python, to reset uncoment lines below
#species_tree_file <- "tl_project.labeled_species_tree.nhxx.corrected"
#numbers_file <- "numbers_reconciliation.tsv"

## Step 1: Read and process your tree
newick_string <- paste(readLines(species_tree_file), collapse = "")
tree <- read.nhx(textConnection(newick_string))

# Reading and combining datan
Datos <- read.table(numbers_file, header = TRUE)
Datos <- Datos %>%
  mutate(Speciation_genes = speciation_roots + genes_at_speciation) %>%
  mutate(Gainss = speciation_roots + duplication_roots)

# Merge additional data with tree data based on the node ID
tree_data <- tree@data
tree_data_combined <- left_join(tree_data, Datos, by = "node_id")
tree@data <- tree_data_combined

# Function to calculate the maximum depth of internal nodes in the tree
calculate_max_depth_internal <- function(tree) {
  # Convert the `treedata` object to `phylo` if needed
  if (inherits(tree, "treedata")) {
    tree <- as.phylo(tree)
  }

  num_tips <- length(tree$tip.label)
  edge_matrix <- tree$edge

  # Helper function to calculate node depth recursively
  calculate_depth <- function(node, tree_edges, num_tips) {
    # If the node is a tip, the depth is 0
    if (node <= num_tips) {
      return(0)
    }

    # Find child nodes of the current node
    child_nodes <- tree_edges[tree_edges[, 1] == node, 2]

    # Calculate the depth of each child and return the maximum
    depths <- sapply(child_nodes, function(child) calculate_depth(child, tree_edges, num_tips))

    # Return the maximum depth of children + 1 for the current node
    return(max(depths) + 1)
  }

  # Calculate the maximum depth of all internal nodes (non-tips)
  depths <- sapply((num_tips + 1):(num_tips + tree$Nnode), function(node) calculate_depth(node, edge_matrix, num_tips))

  # Return the maximum depth of internal nodes
  return(max(depths) - 1)
}

# Function to calculate the number of species (tips) in the tree
calculate_num_species <- function(tree) {
  # Convert the `treedata` object to `phylo` if needed
  if (inherits(tree, "treedata")) {
    tree <- as.phylo(tree)
  }

  # The number of species is the number of tips (leaves) in the tree
  return(length(tree$tip.label))
}

# Calculate the number of species and the maximum depth of the tree
num_species <- as.numeric(calculate_num_species(tree))
max_depth <- as.numeric(calculate_max_depth_internal(tree))

# Predefined data for node-depth limits
limits_table <- data.frame(
  Nodos = 0:14,
  Limits = c(1.2, 2.5, 3.5, 4.7, 5.7, 6.7, 8, 9, 10, 11, 12, 13, 14, 15.3, 16.3)
)

# Fit a linear regression model for dynamic x-axis limits
lm_model <- lm(Limits ~ Nodos, data = limits_table)

# Function to calculate the x-axis limit dynamically based on max depth
get_plot_limit <- function(max_depth) {
  if (max_depth >= 0) {  # Ensure max_depth is valid
    # Predict the limit using the regression model
    limit_value <- predict(lm_model, newdata = data.frame(Nodos = max_depth))
    return(limit_value)
  } else {
    stop("max_depth must be greater than or equal to 0.")
  }
}

# Get the dynamic plot limit
plot_limit <- get_plot_limit(max_depth)

# Create the tree plot with ggtree
p <- ggtree(tree, ladderize = FALSE) +
  geom_tree(size = 1) +  # Draw the tree structure
  geom_tiplab(size = 4, vjust = 0.5) +  # Add labels for the tips
  geom_text(aes(x = branch, label = Speciation_genes), size = 4, vjust = -0.2, hjust = 1.3, color = "black") +  # Add branch labels
  scale_x_continuous(limits = c(0, plot_limit)) +  # Set the x-axis limit dynamically
  coord_cartesian(ylim = c(1, ifelse(num_species > 20, num_species + 1, num_species))) +  # Adjust y-axis limit based on species count
  theme(
    panel.grid = element_blank()  # Remove grid lines from the plot
  )

#################################################################################
'''

modules['Module_3']= '''############################################
# Module 3 | Calculations and prepare data #
############################################

# This script will be called by the python program revolutionhtl.plot_summary

# Calculation of gains, losses, and duplications

tree_data <- tree_data_combined %>%
  mutate(
    total = gene_gain_by_duplication + gene_loss + (duplication_roots + speciation_roots),
    Duplications = if_else(total != 0, gene_gain_by_duplication / total, 0),
    Losses = if_else(total != 0, gene_loss / total, 0),
    Gains = if_else(total != 0, Gainss / total, 0)
  ) %>%
  filter(!is.na(Gains), !is.na(Losses), !is.na(Duplications), !is.na(node_id))

####### Parent and children
edges <- tree@phylo$edge  # Parent-child relationship matrix (parent, child)
colnames(edges) <- c("Parent", "Child")

# Convert edges to a data frame
edges_df <- as.data.frame(edges)

# Join "edges_df" with "tree_data" to retrieve "node_id" corresponding to "node"
edges_df <- edges_df %>%
  left_join(tree_data %>% select(node, node_id), by = c("Parent" = "node")) %>%
  mutate(Parent = ifelse(!is.na(node_id), node_id, Parent)) %>%
  select(-node_id)  # Remove 'node_id' column after replacement

# Join "edges_df" with "tree_data" to retrieve "node_id" corresponding to "Child"
edges_df <- edges_df %>%
  left_join(tree_data %>% select(node, node_id), by = c("Child" = "node")) %>%
  mutate(Child = ifelse(!is.na(node_id), node_id, Child)) %>%
  select(-node_id)  # Remove "node_id" column after replacement

# Create a data frame to associate nodes with parent information
father_info <- tree@data %>%
  mutate(Child = node_id) %>%  # Rename node to Child to match with edges
  select(Child, gene_gain_by_duplication)  # Select node and relevant information

# Combine parent information with the original tree
tree@data <- tree@data %>%
  left_join(edges_df, by = c("node_id" = "Child")) %>%  # Add 'Parent' column
  left_join(father_info, by = c("Parent" = "Child"), suffix = c("", "_father")) %>%  # Add parent information
  rename(father_node = gene_gain_by_duplication_father)

# Recursive function to get all ancestors (parents) of a node
get_all_parents <- function(node, edges_df) {
  # Find the immediate parent
  parents <- edges_df %>%
    filter(Child == node) %>%
    pull(Parent)

  # If no parents, return an empty list
  if (length(parents) == 0) {
    return(NULL)
  }

  # If parents exist, recursively find all ancestors
  all_parents <- parents
  for (parent in parents) {
    # Recursive call to find parents of each parent
    all_parents <- c(all_parents, get_all_parents(parent, edges_df))
  }

  # Return all unique ancestors
  return(unique(all_parents))
}

# Apply the function to retrieve all ancestors (parents)
tree_data_with_all_parents <- tree_data %>%
  rowwise() %>%
  mutate(fathers = list(get_all_parents(node_id, edges_df)))

####### Calculate de novo and ancestral

# Create a new 'total' column by summing values for each row
tree_data_with_all_parents$total <- sapply(seq_along(tree_data_with_all_parents$fathers), function(i) {
  # Extract the current element from "fathers"
  fathers_list <- tree_data_with_all_parents$fathers[[i]]
  own_value <- tree_data_with_all_parents$gene_gain_by_duplication[i]

  # Check if 'fathers_list' is NULL or empty
  if (is.null(fathers_list) || length(fathers_list) == 0) {
    return(own_value)  # If no parents, return own value
  }

  # Convert the list of parents to numeric
  temp_fathers <- as.numeric(fathers_list)

  # Match with node_id and sum "gene_gain_by_duplication"
  temp_sum <- sum(
    tree_data_with_all_parents$gene_gain_by_duplication[
      tree_data_with_all_parents$node_id %in% fathers_list
    ],
    na.rm = TRUE
  )
  return(temp_sum + own_value)  # Return the sum of parents and own value
})

# Add new columns "de_novo" and "ancestral"
tree_data_with_all_parents <- tree_data_with_all_parents %>%
  mutate(
    Novo = (gene_gain_by_duplication / total) * 100,  # Calculate "de_novo"
    Ancestral = 100 - Novo                           # Calculate "ancestral"
  )

# Prepare data for heatmap
heatmap_data_full <- tree_data_with_all_parents %>%
  select(node, Gains, Losses, Duplications) %>%
  pivot_longer(cols = c("Gains", "Losses", "Duplications"), names_to = "variable", values_to = "value") %>%
  group_by(variable) %>%
  mutate(
    min_value = min(value, na.rm = TRUE),
    max_value = max(value, na.rm = TRUE),
    normalized_value = (value - min_value) / (max_value - min_value)
  ) %>%
  ungroup()

#################################################################################
'''


modules['Module_4']= '''### Module 4
### Calculations and prepare data
# Prepare heatmaps

# Calculate log2_deviation_min and log2_deviation_max
log_min <- min(heatmap_data_full$normalized_value, na.rm = TRUE)
log_max <- max(heatmap_data_full$normalized_value, na.rm = TRUE)

colors <- c("#B1D690", "#FCF596", "#FF4545")

# Determine Max value
max_data_value <- tree_data %>%
  select(gene_gain_by_duplication, gene_loss, duplication_roots) %>%
  summarise(across(everything(), max)) %>%
  unlist() %>%
  max()


if (nchar(as.character(max_data_value)) > 4 || num_species > 13) {
  wsize <- 2.5
} else {
  wsize <- 3.5
}


# Custom function to create combined plots for each node
custom_node_combined_plot <- function(data, heatmap_cols, bar_cols, log_min, log_max, num_species, color_palette = NULL) {

  heatmap_data <<- data %>%
    select(node, all_of(heatmap_cols), duplication_roots, gene_gain_by_duplication, gene_loss) %>%
    pivot_longer(cols = all_of(heatmap_cols), names_to = "variable", values_to = "value") %>%
    group_by(variable) %>%
    mutate(
      min_value = min(value, na.rm = TRUE),
      max_value = max(value, na.rm = TRUE),
      normalized_value = (value - min_value) / (max_value - min_value)
    ) %>%
    ungroup()

  # Create count data in long format for the heatmap
  counts_data <<- data %>%
    select(node,
           Gains = Gainss,
           Duplications = gene_gain_by_duplication,
           Losses = gene_loss) %>%
    pivot_longer(cols = c("Gains", "Duplications", "Losses"),
                 names_to = 'variable', values_to = 'count')

  # Merge counts with heatmap data
  heatmap_data <<- heatmap_data %>%
    left_join(counts_data, by = c('node', 'variable'))

  # Prepare data for stacked bar plot
  bar_data <<- data %>%
    select(node, all_of(bar_cols)) %>%
    pivot_longer(cols = all_of(bar_cols), names_to = "variable", values_to = "value")

  # Create a list to store the combined plots
  combined_list <<- list()

  # Define the color palette for the heatmap
  if (is.null(color_palette)) {
    color_palette <- rev(RColorBrewer::brewer.pal(11, "RdBu"))
  }

  # Iterate over each node to create the combined plot
  unique_nodes <<- unique(heatmap_data$node)
  for (node_id in unique_nodes) {
    # Heatmap data for the current node
    node_heatmap_data <<- heatmap_data %>% filter(node == node_id)
    # Bar plot data for the current node
    node_bar_data <- bar_data %>% filter(node == node_id)

    # Calculate the total percentage for the current node (should be 1)
    total_value <- sum(node_bar_data$value, na.rm = TRUE)

    # Add column to identify the segment with the highest value
    node_bar_data <- node_bar_data %>%
      mutate(
        percentage = (value / total_value) * 100,  # Convert to percentage
        is_max = value == max(value, na.rm = TRUE)
      )

    if (num_species > 16) {
      p_heatmap <- ggplot(node_heatmap_data, aes(x = variable, y = 1, fill = normalized_value)) +
        geom_tile(color = "black",
                  width = 1,  # Adjust tile size
                  height = 0.6) +  # Adjust tile height
        geom_text(aes(label = ""),  # Do not show numbers if num_species > 20
                  size = wsize, fontface = "bold", color = "black") +
        scale_fill_gradientn(
          colors = colors,  # Custom color palette
          values = scales::rescale(c(0, 0.5, 1), to = c(0, 1)),  # Scale values from 0 to 1
          limits = c(0, 1),  # Limit values between 0 and 1
          na.value = "white",  # Assign NA values to white to avoid gray
          name = "Normalized Value"
        ) +
        theme_void() +
        theme(legend.position = "none",
              axis.text.y = element_blank(),
              axis.text.x = element_blank(),
              plot.margin = margin(0, 0, 0, 0)) +  # Remove additional margins
        coord_fixed(ratio = 1)  # Maintain square aspect ratio

    } else {
      # If num_species <= 20, show numbers
      p_heatmap <- ggplot(node_heatmap_data, aes(x = variable, y = 1, fill = normalized_value)) +
        geom_tile(color = "black",
                  width = 1,  # Adjust tile size
                  height = 0.6) +  # Adjust tile height
        geom_text(aes(label = count),  # Show numbers if num_species <= 20
                  size = wsize, fontface = "bold", color = "black") +
        scale_fill_gradientn(
          colors = colors,  # Custom color palette
          values = scales::rescale(c(0, 0.5, 1), to = c(0, 1)),  # Scale values from 0 to 1
          limits = c(0, 1),  # Limit values between 0 and 1
          na.value = "white",  # Assign NA values to white to avoid gray
          name = "Normalized Value"
        ) +
        theme_void() +
        theme(legend.position = "none",
              axis.text.y = element_blank(),
              axis.text.x = element_blank(),
              plot.margin = margin(0, 0, 0, 0)) +  # Remove additional margins
        coord_fixed(ratio = 1)  # Maintain square aspect ratio
    }


    p_bar <- NULL
    if (num_species <= 25) {
      p_bar <- ggplot(node_bar_data, aes(x = 1, y = value, fill = variable)) +
        geom_bar(stat = "identity", width = 1) +
        geom_text(
          data = node_bar_data %>% filter(is_max),
          aes(label = paste0(round(percentage, 0), "%"), y = value / 2),
          color = "black", size = 3.5, fontface = "bold"
        ) +
        scale_fill_manual(values = c("Novo" = "#66C2A5", "Ancestral" = "#FC8D62"), name = "Duplications") +
        theme_void() +
        coord_polar("y") +  # Use polar coordinates for circular plot
        theme(legend.position = "none", plot.margin = margin(0, 0, 0, 0))  # Remove margins in circular plot
    }



    # Combine the heatmap and bar plot (if exists)
    if (!is.null(p_bar) & num_species < 16) {
      combined_plot <- grid.arrange(p_heatmap, p_bar, ncol = 1, heights = c(1, 1))
    } else if (!is.null(p_bar) & num_species >= 16) {
      combined_plot <- grid.arrange(p_heatmap, p_bar, nrow = 1, widths = c(1.7, 1))
    } else {
      combined_plot <- p_heatmap
    }

    # Add the combined plot to the list
    combined_list[[as.character(node_id)]] <- combined_plot
  }

  return(combined_list)
}

# Create the combined plots for each node, passing the num_species variable
combined_plots <- custom_node_combined_plot(
  data = tree_data_with_all_parents,
  heatmap_cols = c("Gains", "Losses", "Duplications"),
  bar_cols = c("Novo", "Ancestral"),
  log_min = log_min,
  log_max = log_max,
  num_species = num_species  # Use the num_species variable
)

# Create the final plot with the combined plots inserted
# Define a list of parameters for each range of species
params_list <- list(
  list(min_species = 101, width = 0.028, height = 0.028, hjust = 0.15, vjust = -0.4),
  list(min_species = 91,  width = 0.030, height = 0.030, hjust = 0.15, vjust = -0.4),
  list(min_species = 81,  width = 0.032, height = 0.032, hjust = 0.15, vjust = -0.4),
  list(min_species = 71,  width = 0.035, height = 0.035, hjust = 0.15, vjust = -0.4),
  list(min_species = 61,  width = 0.04,  height = 0.04,  hjust = 0.15, vjust = -0.4),
  list(min_species = 41,  width = 0.05,  height = 0.05,  hjust = 0.2,  vjust = -0.35),
  list(min_species = 31,  width = 0.06,  height = 0.06,  hjust = 0.2,  vjust = -0.3),
  list(min_species = 26,  width = 0.08,  height = 0.08,  hjust = 0.2,  vjust = -0.3),
  list(min_species = 16,  width = 0.1,   height = 0.1,   hjust = 0.12, vjust = -0.25),
  list(min_species = 14,  width = 0.08,  height = 0.08,  hjust = 0.07, vjust = -0.02),
  list(min_species = 11,  width = 0.1,   height = 0.1,   hjust = 0.07, vjust = -0.02),
  list(min_species = 6,   width = 0.12,  height = 0.12,  hjust = 0.07, vjust = -0.05),
  list(min_species = 0,   width = 0.15,  height = 0.15,  hjust = 0.02, vjust = -0.01)
)

# Find the parameters that match the current number of species
selected_params <- params_list[[which.max(sapply(params_list, function(x) num_species >= x$min_species))]]

# Use the selected parameters to create the final plot
final_plot <- inset(p, combined_plots,
                    width = selected_params$width,
                    height = selected_params$height,
                    hjust = selected_params$hjust,
                    vjust = selected_params$vjust)

#################################################################################
'''
modules['Module_5']= '''### Module 5
### Bar plot
# Prepare data

bars_log <- FALSE

df_change_new <- p[["data"]] %>%
  filter(!is.na(label)) %>%
  mutate(Change_gene_content = duplication_roots + speciation_roots + gene_gain_by_duplication - gene_loss) %>%
  select(label, Change_gene_content) %>%
  gather(key = "category", value = "value", -label)

# Get non-NA values for label
label_order <- unique(na.omit(p[["data"]]$label))
label_order <- rev(label_order)  # Reverse the order

# Now use this order in the 'label' column
df_change_new$label <- factor(df_change_new$label, levels = label_order)

#
if (num_species >= 2 && num_species <= 5) {
  bar_width <- 0.2
} else if (num_species > 5 && num_species <= 10) {
  bar_width <- 0.3
} else {
  bar_width <- 0.5
}
#

# Plot the result

p_bar1 <- ggplot(df_change_new, aes(x = value, y = category)) +
  geom_bar(
    aes(fill = value > 0),  # Conditional coloring based on whether the value is positive or negative
    stat = "identity",
    width = bar_width
  ) +
  scale_fill_manual(
    values = c("#B03052", "#4f93fcff"),  # Dark red for negative values, blue for positive ones
    name = "Sign"
  ) +
  # Vertical line at x = 0
  geom_vline(
    xintercept = 0,
    color = "black",  # Black line
    linewidth = 1     # Line thickness
  ) +
  facet_wrap(~ label, ncol = 1) +
  theme_minimal() +
  theme(
    legend.position = "none",               # Remove legend
    panel.grid = element_blank(),           # Remove grid
    strip.text = element_blank(),           # Remove facet titles
    axis.text.y = element_blank(),          # Remove Y-axis text
    axis.title.y = element_blank(),         # Remove Y-axis title
    axis.title.x = element_blank(),  # Adjust X-axis title size
    plot.title = element_text(size = 15, hjust = 0.5)
  ) +
  ggtitle("Change gene content")

# Combine the tree plot with the bar plot
final_plot <- plot_grid(final_plot, p_bar1, rel_widths = c(5, 1))

print(final_plot)

#################################################################################
'''

modules['Module_6']= '''#####################################
# Module 6 | Legends and save plots #
#####################################

# This script will be called by the python program revolutionhtl.plot_summary
# The variables bellow are suposed to be created by python, to reset uncoment lines below
#o_format <- "pdf"
#prefix <- "tl_project."

oname <- paste(prefix, "change_in_gene_content.", "pdf",sep="")

# Prepare data
heatmap_legend_data <- data.frame(
  variable = c("Gains", "Losses", "Duplications"),
  log2_deviation = seq(log_min, log_max, length.out = 3)
)

heatmap_legend_plot <- ggplot() +
  geom_tile(
    data = heatmap_legend_data,
    aes(x = variable, y = 1),
    fill = "white",
    color = "black"
  ) +
  geom_tile(
    data = heatmap_legend_data,
    aes(x = variable, y = 1, fill = log_min),
    alpha = 0
  ) +
  scale_fill_gradientn(
    colors = c("#B1D690", "#FCF596", "#FF4545"),
    values = scales::rescale(c(0, 0.5, 1), to = c(0, 1)),
    limits = c(log_min, log_max),
    name = "Normalized Counts",
    na.value = "white",
    labels = c("0", "0.25", "0.5", "0.75", "1"),
    breaks = seq(log_min, log_max, length.out = 5),
    guide = guide_colorbar(
      title.position = "top",
      title.hjust = 0.5
    )
  ) +
  theme_minimal() +
  theme(
    axis.title.x = element_blank(),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
    axis.title.y = element_blank(),
    axis.text.y = element_blank(),
    panel.grid = element_blank(),
    plot.title = element_text(size = 15, hjust = 0.5),
    legend.position = "bottom",
    legend.direction = "horizontal"
  ) +
  ggtitle("Event Counts")

# Legend for the stacked bar plot with variable names
bar_legend_data <- data.frame(
  variable = factor(c("Novo", "Ancestral"), levels = c("Novo", "Ancestral")),
  value = c(0, 0)
)

bar_legend_plot <- ggplot(bar_legend_data, aes(x = 1, y = value, fill = variable)) +
  geom_bar(stat = "identity") +
  scale_fill_manual(
    values = c("Novo" = "#66C2A5", "Ancestral" = "#FC8D62"),
    name = "Duplications"
  ) +
  theme_minimal() +
  theme(
    axis.title.x = element_blank(),
    axis.text.x = element_blank(),
    axis.title.y = element_blank(),
    axis.text.y = element_blank(),
    panel.grid = element_blank()
  )

# Combine the final plot with adjusted legends
if (num_species > 20) {
  # If num_species is greater than 20, exclude bar_legend_plot
  blank_legend <- cowplot::ggdraw() + cowplot::draw_label("", size = 0)  # Blank space

  combined_with_legends <- cowplot::plot_grid(
    final_plot,
    cowplot::plot_grid(heatmap_legend_plot, blank_legend, ncol = 1, rel_heights = c(0.1, 0.3)),  # Include blank instead of bar_legend_plot
    ncol = 2,
    rel_widths = c(9, 1)  # Adjust width of the legend column
  )
} else {
  # If num_species is 20 or less, include bar_legend_plot
  combined_with_legends <- cowplot::plot_grid(
    final_plot,
    cowplot::plot_grid(heatmap_legend_plot, bar_legend_plot, ncol = 1, rel_heights = c(0.1, 0.3)),  # Include both legends
    ncol = 2,
    rel_widths = c(9, 1)  # Adjust width of the legend column
  )
}
# Display the combined plot with legends
# print(final_plot)
print(combined_with_legends)

# Save
ggsave(oname, plot = combined_with_legends, device = "pdf", width = 16, height = 10)
print(paste('Written to ', oname))

#################################################################################
'''

modules= Series(modules)
