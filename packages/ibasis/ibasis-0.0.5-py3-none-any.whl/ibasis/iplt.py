import matplotlib.pyplot as plt


def show_img_lis(imgs, figsize=(7, 3), rows=2, cols=3):
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    for i in range(rows):
        for j in range(cols):
            axes[i, j].imshow(imgs[i * cols + j])
            axes[i, j].axis('off')

    fig.tight_layout()
    return fig
