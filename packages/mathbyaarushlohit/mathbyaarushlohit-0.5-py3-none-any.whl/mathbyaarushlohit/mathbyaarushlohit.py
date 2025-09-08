
# -------------------------
# numpy check
# -------------------------
try:
    import numpy as np
except ImportError:
    raise ImportError(
        "This module requires numpy. Install it with: pip install numpy"
    )


def eigenkvalues(matrix, threshold=0.90):
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    variance_explained = eigenvalues / np.sum(eigenvalues)
    cumulative_variance = np.cumsum(variance_explained)
    k = np.argmax(cumulative_variance >= threshold) + 1
    principal_components = eigenvectors[:, :k]

    print("Eigenvalues:", eigenvalues)
    print("Eigenvectors:\n", eigenvectors)
    print("Variance Explained:", variance_explained)
    print("Cumulative Variance:", cumulative_variance)
    print("Number of Components Selected (k):", k)
    print("Top k Principal Components:\n", principal_components)
    return ""
    
def credits():
    print("This module is developed by Aarush Lohit. Follow me on GitHub: github.com/aarushlohit, Instagram: @aarushlohit_01")
    print("This is designed to help biology-background students and coding slow learners achieve better marks in internal exams 🌟, reduce stress 😌, and overcome inferiority complex 💪.")
    print("Aarush Lohit – (ALC²) 👑")
    
# Story behind this project:
    print('''  
    🌐 Lohit-Cybersecurity (ALC²-Author|Lyricist|Coder|Cybersec) 🚀
    Hey, I’m Aarush Lohit, a CSE student with a passion for coding. I also write lyrics 🎶 and am a Spotify Artist with a song named *THIRUMBHI VARUVAYO*—search it up on Google and you'll find it! 
    I noticed many CSE students struggling with coding... 😓
    So, I created a special module to make it easier for them to learn. 📚
    I came like a superhero 🦸 to make coding simple and fun! 🎉
    No more fear of errors or confusion in programs 🔥.
    I gave students the support they needed to grow and thrive 🌱.
    This project isn't just code; it’s a helping hand 🤝.
    And I’m proud to be the one who built it! 🙌
        ''')
def answereigenkvalues():
        line = "-" * 150
        print(line.center(170))
        print(line.center(170))
        code = '''
    # PCA from Scratch: Eigenvalues and Eigenvectors Calculation
    #Full Source Code: Copy paste and run it //

    import numpy as np
    # Covariance Matrix
    # change the values in the covariance matrix as per your requirement dont blindly run the code
    cov_matrix = np.array([[4, 2],
                        [2, 3]])

    # Step 1: Compute Eigenvalues and Eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

    # Step 2: Sort Eigenvalues and Eigenvectors in Descending Order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Step 3: Proportion of Variance Explained
    variance_explained = eigenvalues / np.sum(eigenvalues)
    cumulative_variance = np.cumsum(variance_explained)

    # Step 4: Select top k components (retain ≥ 90% variance)
    threshold = 0.90
    k = np.argmax(cumulative_variance >= threshold) + 1

    # Step 5: Extract top k principal components
    principal_components = eigenvectors[:, :k]

    # Display Results
    print("Eigenvalues:", eigenvalues)
    print("Eigenvectors:\\n", eigenvectors)
    print("Variance Explained:", variance_explained)
    print("Cumulative Variance:", cumulative_variance)
    print(f"Number of Components Selected (k): {k}")
    print("Top k Principal Components:\\n", principal_components)
    '''
        print(code)
        # No return needed, function prints output

    # Move the function definition outside of credits() and place it at module level

if __name__ == "__main__":
    credits()
    #eigenkvalues([[4, 2], [2, 3]])
   # answereigenkvalues()
    