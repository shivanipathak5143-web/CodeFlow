export function saveBlob(blob: Blob, name: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/** Mermaid text without the `click` lines (those are only meaningful inside this app). */
export function portableMermaid(code: string): string {
  return code
    .split("\n")
    .filter((l) => !l.trim().startsWith("click "))
    .join("\n");
}

export function readmeBlock(code: string): string {
  return "## Architecture\n\n```mermaid\n" + portableMermaid(code) + "\n```\n";
}

export function svgToPng(svg: SVGSVGElement, background = "#0e0d0b"): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const box = svg.getBoundingClientRect();
    const clone = svg.cloneNode(true) as SVGSVGElement;
    clone.setAttribute("width", String(box.width));
    clone.setAttribute("height", String(box.height));
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(box.width * 2));
      canvas.height = Math.max(1, Math.round(box.height * 2));
      const ctx = canvas.getContext("2d");
      if (!ctx) return reject(new Error("Canvas is not available"));
      ctx.fillStyle = background;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("PNG export failed"))), "image/png");
    };
    img.onerror = () => reject(new Error("Could not render the diagram to an image"));
    img.src =
      "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new XMLSerializer().serializeToString(clone));
  });
}