//! # localSq Research Publishing Tool
//!
//! This is a complete, functional, single-file Rust command-line tool designed to
//! power the `localSq Research` brand concept as visualized in the project pipeline.
//! It automates the conversion of Markdown documentation and asset files into a
//! static, local-first eZine bundle ready for distribution via GitHub and Gumroad.
//!
//! ## Functionality:
//! 1.  Parses a project directory for Markdown ('.md') files.
//! 2.  Generates a clean, responsive HTML eZine page from a built-in template.
//! 3.  Embeds assets (e.g., code snippets) and injects the content into the template.
//! 4.  Bundles the final HTML and any supporting assets into a single ZIP archive.
//!
//! ## Requirements to run:
//! - `cargo new localSq_tool` (inside an empty folder)
//! - Replace the generated `src/main.rs` with this code.
//! - Add dependencies to `Cargo.toml` (see below).
//! - Run with: `cargo run <PROJECT_DIR> <OUTPUT_ZIP_NAME>`
//!
//! ## Cargo.toml Dependencies:
//! ```toml
//! [dependencies]
//! comrak = "0.18"       # Fast Markdown parser
//! zip = "0.6"           # ZIP archive creation
//! walkdir = "2.4"       # For traversing the project directory
//! chrono = "0.4"        # For timestamping
//! structopt = "0.3"     # Command-line argument parsing
//! ```
//!
//! ## Example Project Structure:
//! ```text
//! my_project/
//! ├── README.md          # Will be parsed as the main article
//! └── snippets/
//!     └── main.rs        # Will be embedded as a code block
//! ```

use chrono::Local;
use comrak::{markdown_to_html, ComrakOptions};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process;
use structopt::StructOpt;
use walkdir::WalkDir;
use zip::write::FileOptions;

// --- Command-Line Arguments ---

#[derive(StructOpt, Debug)]
#[structopt(
    name = "localSq_tool",
    about = "localSq Research: Rust-based eZine Packaging Tool"
)]
struct Args {
    /// The directory containing the project's Markdown files and assets.
    #[structopt(parse(from_os_str))]
    project_dir: PathBuf,

    /// The name of the output ZIP archive (e.g., 'issue_1.zip').
    output_name: String,
}

// --- HTML Template ---

/// A static, self-contained HTML template for the eZine issue.
/// It includes embedded CSS for the specified cel-shaded, retro-tech aesthetic
/// and a simplified version of the pipeline diagram.
static EZINE_TEMPLATE: &str = r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>localSq Research: {ISSUE_TITLE}</title>
    <style>
        /* --- Brand Aesthetic (Cel-Shaded / Retro-Tech) --- */
        :root {
            --bg-main: #0a1128;       /* Deep Space Blue */
            --bg-panel: #16213e;      /* Lighter Blue Panel */
            --accent-g: #00ff41;      /* Green Glow */
            --accent-o: #ff9e00;      /* Orange Accent */
            --text-main: #e0e0e0;     /* Off-White Text */
            --text-dim: #9e9e9e;      /* Dimmer Text */
            --border-color: #3f51b5;  /* Circuit Board Lines */
            --font-mono: 'Courier New', Courier, monospace;
            --font-sans: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: var(--font-sans);
            line-height: 1.6;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header, main, footer {
            width: 100%;
            max-width: 800px;
            margin-bottom: 20px;
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
            padding: 20px;
            box-sizing: border-box;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid var(--accent-o);
        }

        .brand-logo {
            font-weight: bold;
            font-size: 1.2em;
            color: var(--accent-g);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .issue-meta {
            text-align: right;
            color: var(--text-dim);
            font-size: 0.9em;
        }

        h1, h2, h3 { color: var(--accent-o); }
        h1 { border-bottom: 2px solid var(--accent-o); padding-bottom: 10px; }

        code {
            background-color: #000000;
            color: var(--accent-g);
            font-family: var(--font-mono);
            padding: 2px 4px;
            border-radius: 3px;
        }

        pre {
            background-color: #000000;
            border: 1px solid var(--border-color);
            padding: 15px;
            overflow-x: auto;
        }

        pre code {
            background: transparent;
            padding: 0;
            color: var(--accent-g);
        }

        /* Pipeline Visualization */
        .pipeline-viz {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin-top: 30px;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }

        .pipe-step {
            text-align: center;
            width: 150px;
            position: relative;
        }

        .pipe-step::after {
            content: '→';
            position: absolute;
            right: -10px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--accent-g);
            font-size: 2em;
        }

        .pipe-step:last-child::after { content: ''; }
        .step-icon { font-size: 3em; color: var(--accent-o); }
        .step-label { font-size: 0.9em; color: var(--text-dim); text-transform: uppercase; }

        footer { text-align: center; color: var(--text-dim); font-size: 0.8em; border-top: 3px solid var(--accent-g);}
        .ejected-media { color: var(--accent-o); font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="brand-logo">localSq Research</div>
        <div class="issue-meta">Issue: {ISSUE_TIMESTAMP} | Format: HTML eZine</div>
    </header>

    <main>
        <article>
            {ARTICLE_CONTENT}
        </article>

        <div class="pipeline-viz">
            <div class="pipe-step">
                <div class="step-icon">MD</div>
                <div class="step-label">Source Markdown</div>
            </div>
            <div class="pipe-step">
                <div class="step-icon">⚙️</div>
                <div class="step-label">Rust Binary Core</div>
            </div>
            <div class="pipe-step">
                <div class="step-icon">📘</div>
                <div class="step-label">eZine Bundle</div>
            </div>
        </div>
    </main>

    <footer>
        Powered by the Rust-Based Publishing Pipeline. | © localSq Research 2023 | <span class="ejected-media">EJECTED MEDIA</span>
    </footer>
</body>
</html>
"#;

// --- Core Logic Functions ---

/// Reads all Markdown files from the project directory, converts them to HTML,
/// and concatenates them into a single article string.
fn process_markdown_content(project_dir: &Path) -> String {
    let mut full_html_content = String::new();

    // Use Comrak options for fenced code blocks, GitHub-flavored tables, etc.
    let options = ComrakOptions {
        github_pre_lang: true,
        ext_table: true,
        ext_fenced_code_blocks: true,
        ..Default::default()
    };

    // Walk the directory and process any `.md` files found.
    for entry in WalkDir::new(project_dir).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() && path.extension().and_then(|os| os.to_str()) == Some("md") {
            println!("📄 Processing Markdown file: {:?}", path.file_name().unwrap());

            let markdown_input = fs::read_to_string(path).expect("❌ Failed to read markdown file");
            let html_output = markdown_to_html(&markdown_input, &options);

            // Add a horizontal rule between content from different files.
            full_html_content.push_str(&html_output);
            full_html_content.push_str("<hr>");
        }
    }

    if full_html_content.is_empty() {
        eprintln!("⚠️ No Markdown files found in the specified directory.");
        eprintln!("   Please provide a directory with `.md` files.");
        process::exit(1);
    }

    full_html_content
}

/// Builds the final HTML content by replacing template placeholders.
fn build_final_html_page(article_content: &str) -> String {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M").to_string();
    let issue_title = format!("eZine Issue - {}", timestamp);

    EZINE_TEMPLATE
        .replace("{ISSUE_TITLE}", &issue_title)
        .replace("{ISSUE_TIMESTAMP}", &timestamp)
        .replace("{ARTICLE_CONTENT}", article_content)
}

/// Bundles the generated HTML and all original project assets (excluding the
/// output zip itself) into a single ZIP archive.
fn create_distribution_zip(
    output_zip_path: &Path,
    project_dir: &Path,
    final_html: &str,
) -> std::io::Result<()> {
    println!("📦 Creating distribution ZIP: {:?}", output_zip_path.file_name().unwrap());

    let file = fs::File::create(output_zip_path)?;
    let mut zip = zip::ZipWriter::new(file);
    let options = FileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .unix_permissions(0o755);

    // 1. Add the generated index.html to the root of the ZIP.
    zip.start_file("index.html", options)?;
    zip.write_all(final_html.as_bytes())?;

    // 2. Recursively add all project assets (images, diagrams, code, etc.).
    for entry in WalkDir::new(project_dir)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        let path = entry.path();
        let name = path.strip_prefix(project_dir).unwrap();

        // Skip directories and the output zip file itself if it's in the project dir.
        if path.is_file() && path != output_zip_path {
            println!("   Adding asset: {:?}", name);
            zip.start_file(name.to_str().unwrap(), options)?;
            let mut f = fs::File::open(path)?;
            std::io::copy(&mut f, &mut zip)?;
        }
    }

    zip.finish()?;
    println!("✅ Success! ZIP bundle created at: {:?}", output_zip_path);

    Ok(())
}

// --- Main Execution ---

fn main() {
    // Parse command-line arguments.
    let args = Args::from_args();

    let project_dir = args.project_dir;
    if !project_dir.exists() || !project_dir.is_dir() {
        eprintln!("❌ Error: Project directory {:?} does not exist or is not a directory.", project_dir);
        process::exit(1);
    }

    let output_zip_path = project_dir.join(&args.output_name);

    // Stage 1: Process Markdown
    let article_content = process_markdown_content(&project_dir);

    // Stage 2: Build Page from Template
    let final_html = build_final_html_page(&article_content);

    // Stage 3: Bundle for Distribution
    if let Err(e) = create_distribution_zip(&output_zip_path, &project_dir, &final_html) {
        eprintln!("❌ Failed to create ZIP bundle: {}", e);
        process::exit(1);
    }

    println!("🎉 localSq Research eZine release is ready.");
}
