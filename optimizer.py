import os
import subprocess

class ImageOptimizer:
    def __init__(self, optipng_path, cwebp_path, jpegoptim_path=None):
        self.optipng_path = optipng_path
        self.cwebp_path = cwebp_path
        self.jpegoptim_path = jpegoptim_path  # facultatif

    def optimize_file(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        log = f"[{filepath}] "
        try:
            if ext == ".png":
                result = subprocess.run([self.optipng_path, "-o7", filepath], capture_output=True, text=True)
                if result.returncode == 0:
                    log += "PNG optimisé avec optipng."
                else:
                    log += f"Erreur optipng: {result.stderr.strip()}"
            elif ext == ".webp":
                # "Optimisation" sans perte = recoder à qualité max (pas toujours utile, mais pour exemple)
                tmpfile = filepath + ".tmp.webp"
                result = subprocess.run([self.cwebp_path, "-lossless", filepath, "-o", tmpfile], capture_output=True, text=True)
                if result.returncode == 0:
                    os.replace(tmpfile, filepath)
                    log += "WebP optimisé avec cwebp."
                else:
                    log += f"Erreur cwebp: {result.stderr.strip()}"
            elif ext in [".jpg", ".jpeg"] and self.jpegoptim_path:
                result = subprocess.run([self.jpegoptim_path, "--strip-all", "--all-progressive", filepath], capture_output=True, text=True)
                if result.returncode == 0:
                    log += "JPEG optimisé avec jpegoptim."
                else:
                    log += f"Erreur jpegoptim: {result.stderr.strip()}"
            else:
                log += "Format non supporté ou exe manquant."
        except Exception as e:
            log += f"Exception: {str(e)}"
        return log

    def optimize_folder(self, folder):
        logs = []
        for root, _, files in os.walk(folder):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in [".png", ".webp"] or (
                    self.jpegoptim_path and ext in [".jpg", ".jpeg"]
                ):
                    path = os.path.join(root, f)
                    logs.append(self.optimize_file(path))
        return logs

# EXEMPLE D'UTILISATION :
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    optipng = os.path.join(base_dir, "tools", "optimizers", "optipng.exe")
    cwebp = os.path.join(base_dir, "tools", "optimizers", "cwebp.exe")
    # jpegoptim facultatif, mets None si tu n’as pas encore l’exe
    optimizer = ImageOptimizer(optipng, cwebp, jpegoptim_path=None)

    dossier_images = r"C:\Users\Lamine\Desktop\images_a_optimiser"  # change le chemin
    logs = optimizer.optimize_folder(dossier_images)
    for l in logs:
        print(l)
