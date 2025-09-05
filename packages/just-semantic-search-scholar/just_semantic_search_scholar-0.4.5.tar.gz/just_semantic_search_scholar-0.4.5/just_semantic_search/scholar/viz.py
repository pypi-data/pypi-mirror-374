from typing import List, Union
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
import typer
from eliot import start_task
from pathlib import Path
from just_semantic_search.embeddings import EmbeddingModel, load_model_from_enum

def visualize_embedding_correlations(
    texts: List[str],
    model: SentenceTransformer = load_model_from_enum(EmbeddingModel.JINA_EMBEDDINGS_V3),
    output_path: Union[str, Path] = "embedding_correlations.png",
    width: int = 800,
    height: int = 600,
    show: bool = True,
    format: str = "png"
) -> None:
    """
    Generate and save a heatmap visualization of correlations between text embeddings.
    """
    with start_task(action_type="viz_corr") as action:
        # Generate embeddings using provided model
        embeddings = model.encode(texts)
        
        # Calculate correlation matrix
        correlation_matrix = np.corrcoef(embeddings)
        
        # Create labels for the texts (removed "Text X:" prefix and ellipsis)
        labels = [text for text in texts]
        
        # Set figure size
        plt.figure(figsize=(width/75, height/75))
        
        # Create heatmap with reversed color scheme and labels on both sides
        ax = sns.heatmap(
            correlation_matrix,
            xticklabels=labels,
            yticklabels=labels,
            cmap='RdBu',
            vmin=0,
            vmax=1,
            center=0.6,
            annot=True,
            fmt='.2f',
            cbar_kws={'pad': 0.2}
        )
        
        # Add labels on right side
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(np.arange(len(labels)) + 0.5)  # Set ticks before labels
        ax2.set_yticklabels(labels, rotation=0)
        
        # Add labels on bottom
        ax3 = ax.twiny()
        ax3.set_xlim(ax.get_xlim())
        ax3.set_xticks(np.arange(len(labels)) + 0.5)  # Set ticks before labels
        ax3.set_xticklabels(labels, rotation=85, ha='center')
        
        # Update original axis labels
        plt.setp(ax.get_yticklabels(), rotation=0)  # Make left labels horizontal
        plt.setp(ax.get_xticklabels(), rotation=85, ha='center')  # Center align top labels
        
        plt.tight_layout(pad=2.0)
        
        # Save figure BEFORE showing it
        print(f"Saving to {output_path}")
        plt.savefig(output_path, format=format.lower(), bbox_inches='tight', dpi=100)
            
        # Show the figure after saving
        if show:
            plt.show()
            
        plt.close()

app = typer.Typer()

def viz_corr(
    input_file: Path = typer.Argument(..., help="Text file with one text per line"),
    model: EmbeddingModel = typer.Option(EmbeddingModel.JINA_EMBEDDINGS_V3, help="Name of the embedding model to use"),
    output_path: Path = typer.Option("embedding_correlations.html", help="Output path for visualization (HTML)"),
    width: int = typer.Option(800, help="Plot width in pixels"),
    height: int = typer.Option(800, help="Plot height in pixels")
):
    """
    Generate an interactive visualization of correlations between text embeddings.
    """
    # Load the model
    #model = load_gte_large() if model_name == DEFAULT_EMBEDDING_MODEL_NAME else SentenceTransformer(model_name)
    sentence_transformer_model = load_model_from_enum(model)
    #Jeanne Calment

    # Read texts from file
    with open(input_file, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    
    visualize_embedding_correlations(
        texts=texts,
        model=sentence_transformer_model,
        output_path=output_path,
        width=width,
        height=height
    )
    
    typer.echo(f"Interactive visualization saved to {output_path}")


if __name__ == "__main__":
    model = load_model_from_enum(EmbeddingModel.JINA_EMBEDDINGS_V3)
    general_terms = ["king", "queen", "prince", "princess", "apple", "orange", "cat", "dog", "synchrophasotron", "accelerator"]
    visualize_embedding_correlations(general_terms, model=model, output_path="embedding_correlations_general_terms.png")
    names = [
        "Jeane Calmant",         # typo 1
        "Jeanna Calment",        # typo 2
        "Jeanne Calment",        # correct
        "Alice Johnson",         # random name 1
        "Bob Smith",             # random name 2
        "Carlos Mendoza",        # random name 3
        "queen", 
        "accelerator",
        "synchrophasotron"
    ]
    visualize_embedding_correlations(names, model=model, output_path="embedding_correlations_names.png")
