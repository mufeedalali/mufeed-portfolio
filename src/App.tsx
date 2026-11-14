import heroImg from "./assets/hero.png";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FaGithub,
  FaLinkedin,
  FaEnvelope,
  FaNodeJs,
  FaPython,
  FaDocker,
  FaAws,
  FaReact,
  FaPhp,
  FaBars,
  FaTimes,
  FaExternalLinkAlt,
  FaCode,
  FaPlay,
} from "react-icons/fa";
import {
  SiTypescript,
  SiNextdotjs,
  SiPostgresql,
  SiMongodb,
  SiGithubactions,
  SiRabbitmq,
  SiLangchain,
  SiFastapi,
  SiSymfony,
} from "react-icons/si";
import {
  Download,
  Mail,
  Send,
  MapPin,
  Code2,
  Brain,
  Cloud,
  Sparkles,
  Bot,
  Database,
} from "lucide-react";

// ─── Data ────────────────────────────────────────────────────────────────────

const navLinks = [
  { label: "About", href: "#about" },
  { label: "Skills", href: "#skills" },
  { label: "Projects", href: "#projects" },
  { label: "Achievements", href: "#achievements" },
  { label: "Experience", href: "#experience" },
  { label: "Contact", href: "#contact" },
];

const skillCategories = [
  {
    title: "Backend Development",
    icon: "🔧",
    iconClass: "backend-cat",
    skills: [
      { name: "Node.js", icon: <FaNodeJs /> },
      { name: "TypeScript", icon: <SiTypescript /> },
      { name: "Python", icon: <FaPython /> },
      { name: "PHP", icon: <FaPhp /> },
      { name: "Symfony", icon: <SiSymfony /> },
      { name: "FastAPI", icon: <SiFastapi /> },
    ],
  },
  {
    title: "Frontend & Full-Stack",
    icon: "🎨",
    iconClass: "frontend-cat",
    skills: [
      { name: "React", icon: <FaReact /> },
      { name: "Next.js", icon: <SiNextdotjs /> },
    ],
  },
  {
    title: "AI & Machine Learning",
    icon: "🧠",
    iconClass: "ai-cat",
    skills: [
      { name: "LangChain", icon: <SiLangchain /> },
      { name: "OpenAI API", icon: <Bot size={14} /> },
      { name: "RAG", icon: <Brain size={14} /> },
      { name: "Vector Databases", icon: <Database size={14} /> },
      { name: "ChromaDB", icon: <Sparkles size={14} /> },
    ],
  },
  {
    title: "Databases & Cloud",
    icon: "☁️",
    iconClass: "devops-cat",
    skills: [
      { name: "PostgreSQL", icon: <SiPostgresql /> },
      { name: "MongoDB", icon: <SiMongodb /> },
      { name: "Docker", icon: <FaDocker /> },
      { name: "AWS", icon: <FaAws /> },
      { name: "GitHub Actions", icon: <SiGithubactions /> },
      { name: "RabbitMQ", icon: <SiRabbitmq /> },
    ],
  },
];

const projects = [
  {
    title: "AI Document Assistant",
    description:
      "A production-ready Retrieval-Augmented Generation (RAG) application that lets users search and chat with their documents using Large Language Models. Supports PDF, Word, and plain text ingestion.",
    technologies: ["Python", "LangChain", "OpenAI API", "ChromaDB", "FastAPI", "React"],
    github: "https://github.com/mufeedalali",
    status: "demo",
    previewEmoji: "📄",
    highlights: ["Vector similarity search", "Multi-document indexing", "Streaming chat UI"],
  },
  {
    title: "AI Coding Assistant",
    description:
      "An intelligent developer tool that understands, analyzes, and improves source code. Features context-aware suggestions, code explanation, refactoring, and bug detection powered by LLMs.",
    technologies: ["Node.js", "TypeScript", "OpenAI API", "React"],
    github: "https://github.com/mufeedalali",
    status: "demo",
    previewEmoji: "💻",
    highlights: ["Context-aware code analysis", "Multi-language support", "Real-time suggestions"],
  },
  {
    title: "Scalable Backend Platform",
    description:
      "A robust microservices backend with REST APIs, JWT authentication, database optimization, event-driven messaging, and fully automated deployment pipelines via CI/CD.",
    technologies: ["Node.js", "PostgreSQL", "Docker", "RabbitMQ", "GitHub Actions"],
    github: "https://github.com/mufeedalali",
    status: "demo",
    previewEmoji: "⚡",
    highlights: ["Event-driven architecture", "99.9% uptime SLA", "Auto-scaling CI/CD"],
  },
];

const achievements = [
  {
    title: "RAG Pipeline — AI Document Assistant",
    badge: "featured",
    description:
      "Built an end-to-end Retrieval-Augmented Generation pipeline from scratch. The GIF below shows real document ingestion, vector search, and LLM-powered answers streaming in real-time.",
    technologies: ["LangChain", "ChromaDB", "FastAPI", "OpenAI"],
    codeGif: null,
    demoGif: null,
    githubUrl: "https://github.com/mufeedalali",
    codeSnippet: `# RAG Pipeline Core
def query_documents(question: str) -> str:
    docs = vectorstore.similarity_search(question, k=4)
    context = "\\n".join([d.page_content for d in docs])
    return llm.invoke(f"Context: {context}\\nQ: {question}")`,
  },
  {
    title: "Microservices with RabbitMQ",
    badge: "completed",
    description:
      "Designed and deployed a polyglot microservices architecture with event-driven communication via RabbitMQ, achieving sub-100ms inter-service latency and full Docker orchestration.",
    technologies: ["Node.js", "RabbitMQ", "Docker", "PostgreSQL"],
    codeGif: null,
    demoGif: null,
    githubUrl: "https://github.com/mufeedalali",
    codeSnippet: `// RabbitMQ Publisher
const publishEvent = async (event: string, payload: object) => {
  const channel = await connection.createChannel();
  await channel.assertExchange('events', 'topic', { durable: true });
  channel.publish('events', event, Buffer.from(JSON.stringify(payload)));
};`,
  },
  {
    title: "AI Coding Assistant CLI",
    badge: "featured",
    description:
      "Shipped a developer-facing CLI tool that reads a repository's code, understands context, and provides actionable suggestions. The animation shows a real session analyzing a Node.js API.",
    technologies: ["TypeScript", "OpenAI API", "Node.js"],
    codeGif: null,
    demoGif: null,
    githubUrl: "https://github.com/mufeedalali",
    codeSnippet: `// Intelligent Code Analyzer
const analyzeCode = async (filePath: string) => {
  const code = await fs.readFile(filePath, 'utf8');
  const response = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [
      { role: 'system', content: 'You are an expert code reviewer.' },
      { role: 'user', content: \`Review:\\n\${code}\` }
    ],
    stream: true,
  });
  for await (const chunk of response) process.stdout.write(chunk.choices[0]?.delta?.content ?? '');
};`,
  },
];

const experience = [
  {
    role: "Backend Developer & AI Engineer",
    company: "Freelance / Open Source",
    date: "2023 – Present",
    current: true,
    tasks: [
      "Built AI-powered applications using LangChain, OpenAI API, and RAG pipelines",
      "Designed and deployed scalable REST APIs with Node.js and TypeScript",
      "Implemented microservices with RabbitMQ for real-time event-driven systems",
      "Containerized production services with Docker and automated deployments via GitHub Actions",
      "Optimized PostgreSQL queries reducing response times by 60%",
    ],
  },
  {
    role: "Full-Stack Developer",
    company: "Software Projects",
    date: "2021 – 2023",
    current: false,
    tasks: [
      "Developed full-stack web applications with PHP/Symfony, React, and Next.js",
      "Designed RESTful APIs consumed by web and mobile clients",
      "Integrated third-party APIs and payment gateways",
      "Worked with PostgreSQL and MongoDB for complex data modelling",
      "Improved CI/CD pipelines reducing deployment time by 40%",
    ],
  },
];

// ─── Animated Counter ─────────────────────────────────────────────────────────

function AnimatedCounter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          let start = 0;
          const step = Math.ceil(target / 40);
          const timer = setInterval(() => {
            start += step;
            if (start >= target) {
              setCount(target);
              clearInterval(timer);
            } else {
              setCount(start);
            }
          }, 40);
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);

  return (
    <span ref={ref}>
      {count}
      {suffix}
    </span>
  );
}

// ─── Code Snippet Display ─────────────────────────────────────────────────────

function CodeDisplay({ code }: { code: string }) {
  return (
    <div
      style={{
        background: "#0f172a",
        borderRadius: "8px",
        padding: "16px",
        fontFamily: "'Fira Code', 'JetBrains Mono', 'Courier New', monospace",
        fontSize: "0.78rem",
        lineHeight: "1.7",
        color: "#94a3b8",
        overflowX: "auto",
        textAlign: "left",
      }}
    >
      {code.split("\n").map((line, i) => (
        <div key={i}>
          <span style={{ color: "#475569", marginRight: "12px", userSelect: "none" }}>
            {String(i + 1).padStart(2, " ")}
          </span>
          <span
            dangerouslySetInnerHTML={{
              __html: line
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/(#.*)$/gm, '<span style="color:#475569">$1</span>')
                .replace(
                  /\b(const|let|var|async|await|return|import|from|export|default|function|class|for|of|if|else|new)\b/g,
                  '<span style="color:#c084fc">$1</span>'
                )
                .replace(
                  /\b(def|import|from|return|for|in|await|async|True|False|None|class)\b/g,
                  '<span style="color:#c084fc">$1</span>'
                )
                .replace(/'([^']*)'/g, '<span style="color:#86efac">\'$1\'</span>')
                .replace(/`([^`]*)`/g, '<span style="color:#86efac">`$1`</span>')
                .replace(/"([^"]*)"/g, '<span style="color:#86efac">"$1"</span>')
                .replace(/(\w+)\(/g, '<span style="color:#67e8f9">$1</span>('),
            }}
          />
        </div>
      ))}
    </div>
  );
}

// ─── Demo Modal ───────────────────────────────────────────────────────────────

function DemoModal({ project, onClose }: { project: { title: string }; onClose: () => void }) {
  return (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="modal-content"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>×</button>
        <div style={{ fontSize: "2rem", marginBottom: "16px" }}>🚀</div>
        <h3>Request a Live Demo</h3>
        <p>
          Interested in seeing <strong>{project.title}</strong> live? Send me a message and I'll
          schedule a personalized walkthrough of the full application.
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <a
            href={`mailto:mufeed_alali@outlook.com?subject=Live Demo Request — ${project.title}&body=Hi Mufeed,%0A%0AI'd love to see a live demo of ${project.title}.%0A%0AMy availability:%0A%0AThank you!`}
            className="btn btn-primary"
            style={{ justifyContent: "center" }}
          >
            <Mail size={16} />
            Request via Email
          </a>
          <button
            onClick={onClose}
            className="btn btn-outline"
            style={{ justifyContent: "center" }}
          >
            Maybe Later
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [demoProject, setDemoProject] = useState<{ title: string } | null>(null);
  const [achievementTab, setAchievementTab] = useState<Record<number, "code" | "demo">>(
    {}
  );
  const [formState, setFormState] = useState({ name: "", email: "", subject: "", message: "" });
  const [formSent, setFormSent] = useState(false);

  // Scroll detection
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Intersection Observer for fade-in-up animations
  useEffect(() => {
    const els = document.querySelectorAll(".fade-in-up");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("visible");
        });
      },
      { threshold: 0.15 }
    );
    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    window.location.href = `mailto:mufeed_alali@outlook.com?subject=${encodeURIComponent(formState.subject || "Portfolio Inquiry")}&body=${encodeURIComponent(`Name: ${formState.name}\nEmail: ${formState.email}\n\n${formState.message}`)}`;
    setFormSent(true);
    setTimeout(() => setFormSent(false), 4000);
  };

  const getAchievementTab = (i: number) => achievementTab[i] ?? "code";

  return (
    <>
      {/* ── Navbar ── */}
      <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
        <div className="navbar-inner">
          <span className="nav-logo">MA</span>

          <ul className={`nav-links ${menuOpen ? "open" : ""}`}>
            {navLinks.map((l) => (
              <li key={l.href}>
                <a href={l.href} onClick={() => setMenuOpen(false)}>
                  {l.label}
                </a>
              </li>
            ))}
            <li>
              <a href="/cv.pdf" download className="nav-links a nav-cta">
                <Download size={14} style={{ display: "inline", marginRight: 6 }} />
                Resume
              </a>
            </li>
          </ul>

          <button
            className="mobile-menu-btn"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="hero-section" id="home">
        <div className="hero-bg">
          <div className="hero-grid" />
        </div>

        <div className="hero-content">
          <motion.div
            className="hero-text-wrapper"
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="hero-greeting">
              <span>👋</span>
              Hello, I'm
            </div>

            <h1 className="hero-name">
              Mufeed <span className="gradient-text">Alali</span>
            </h1>

            <p className="hero-role">
              <strong>Backend Developer · AI Engineer</strong>
              <br />
              I build scalable backend systems and AI-powered applications — from
              RAG pipelines and LLM integrations to microservices and cloud deployments.
            </p>

            <div className="hero-buttons">
              <a href="#projects" className="btn btn-primary">
                <Code2 size={16} /> View Projects
              </a>
              <a href="#contact" className="btn btn-outline">
                <Mail size={16} /> Get in Touch
              </a>
              <a href="/cv.pdf" download className="btn btn-outline">
                <Download size={16} /> Resume
              </a>
            </div>

            <div className="hero-socials">
              <a
                href="https://github.com/mufeedalali"
                target="_blank"
                rel="noreferrer"
                className="social-icon"
                aria-label="GitHub"
              >
                <FaGithub />
              </a>
              <a
                href="https://linkedin.com/in/mufeedalali"
                target="_blank"
                rel="noreferrer"
                className="social-icon"
                aria-label="LinkedIn"
              >
                <FaLinkedin />
              </a>
              <a
                href="mailto:mufeed_alali@outlook.com"
                className="social-icon"
                aria-label="Email"
              >
                <FaEnvelope />
              </a>
              <a
                href="#"
                className="social-icon"
                aria-label="Location"
                style={{ cursor: "default" }}
              >
                <MapPin size={18} />
              </a>
            </div>
          </motion.div>

          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="hero-image-wrapper">
              <div className="hero-image-ring" />
              <img
                src={heroImg}
                alt="Mufeed Alali"
                className="hero-image"
                onError={(e) => {
                  // Fallback to text initials if image fails
                  const target = e.currentTarget;
                  target.style.display = "none";
                  const fallback = target.nextElementSibling as HTMLElement;
                  if (fallback) fallback.style.display = "flex";
                }}
              />
              <div
                className="hero-image"
                style={{ display: "none" }}
              >
                MA
              </div>

              <div className="hero-floating-badge top-badge">
                <div className="badge-icon purple">
                  <Brain size={16} />
                </div>
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700 }}>AI Engineer</div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>LLMs & RAG</div>
                </div>
              </div>

              <div className="hero-floating-badge bottom-badge">
                <div className="badge-icon cyan">
                  <Cloud size={16} />
                </div>
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700 }}>Backend Dev</div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Node · Docker · AWS</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Stats Banner ── */}
      <div className="stats-banner">
        <div className="section-wrapper section-padding" style={{ paddingTop: 48, paddingBottom: 48 }}>
          <div className="stats-grid">
            {[
              { number: 3, suffix: "+", label: "Years Experience" },
              { number: 15, suffix: "+", label: "Projects Delivered" },
              { number: 17, suffix: "", label: "Technologies" },
              { number: 100, suffix: "%", label: "Client Satisfaction" },
            ].map((s) => (
              <div key={s.label} className="stat-item">
                <div className="stat-item-number">
                  <AnimatedCounter target={s.number} suffix={s.suffix} />
                </div>
                <div className="stat-item-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── About ── */}
      <section id="about" className="section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">About Me</div>
            <h2 className="section-title">Passionate about building things that scale</h2>
            <p className="section-subtitle">
              Backend developer with a strong focus on AI integration, performance, and clean architecture.
            </p>
          </div>

          <div className="about-grid">
            <div className="about-text fade-in-up">
              <p>
                I'm a software developer specialized in <strong>backend and full-stack development</strong>,
                with a growing expertise in <strong>AI engineering</strong>. I love turning complex
                problems into elegant, performant solutions.
              </p>
              <p>
                My work spans from designing distributed backend systems with{" "}
                <strong>Node.js, TypeScript, and PostgreSQL</strong>, to building intelligent
                AI-powered applications with <strong>LangChain, OpenAI API, and RAG pipelines</strong>.
              </p>
              <p>
                When I'm not coding, I'm exploring new AI research, contributing to open source,
                or learning the latest in cloud-native architecture. I believe great software is
                built at the intersection of engineering rigor and creative problem-solving.
              </p>

              <div className="about-stats">
                {[
                  { number: 3, suffix: "+", label: "Years Coding" },
                  { number: 15, suffix: "+", label: "Projects" },
                  { number: 5, suffix: "+", label: "AI Apps Built" },
                ].map((s) => (
                  <div key={s.label} className="stat-card">
                    <div className="stat-number">
                      <AnimatedCounter target={s.number} suffix={s.suffix} />
                    </div>
                    <div className="stat-label">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="about-highlights fade-in-up stagger-2">
              {[
                {
                  icon: <Code2 size={22} />,
                  iconClass: "backend",
                  title: "Backend Architecture",
                  desc: "Designing scalable REST APIs, microservices, and event-driven systems with Node.js, TypeScript, and Python.",
                },
                {
                  icon: <Brain size={22} />,
                  iconClass: "ai",
                  title: "AI & LLM Engineering",
                  desc: "Building production RAG systems, AI assistants, and LLM-powered tools using LangChain and the OpenAI ecosystem.",
                },
                {
                  icon: <Cloud size={22} />,
                  iconClass: "cloud",
                  title: "Cloud & DevOps",
                  desc: "Containerizing applications with Docker, deploying on AWS, and automating pipelines with GitHub Actions.",
                },
              ].map((h) => (
                <div key={h.title} className="highlight-card">
                  <div className={`highlight-icon ${h.iconClass}`}>{h.icon}</div>
                  <div className="highlight-info">
                    <h4>{h.title}</h4>
                    <p>{h.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Skills ── */}
      <section id="skills" className="skills-section section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">Tech Stack</div>
            <h2 className="section-title">Skills & Technologies</h2>
            <p className="section-subtitle">
              A curated set of tools I use to build robust, intelligent software.
            </p>
          </div>

          <div className="skills-categories">
            {skillCategories.map((cat, i) => (
              <div key={cat.title} className={`skill-category fade-in-up stagger-${i + 1}`}>
                <div className="skill-category-header">
                  <div className={`skill-category-icon ${cat.iconClass}`}>{cat.icon}</div>
                  <h3 className="skill-category-title">{cat.title}</h3>
                </div>
                <div className="skill-items">
                  {cat.skills.map((s) => (
                    <span key={s.name} className="skill-tag">
                      {s.icon}
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Projects ── */}
      <section id="projects" className="section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">Portfolio</div>
            <h2 className="section-title">Featured Projects</h2>
            <p className="section-subtitle">
              A selection of projects I've built — from AI pipelines to scalable backend platforms.
            </p>
          </div>

          <div className="projects-grid">
            {projects.map((project, i) => (
              <motion.div
                key={project.title}
                className="project-card fade-in-up"
                style={{ animationDelay: `${i * 0.1}s` }}
                whileHover={{ y: -6 }}
                transition={{ duration: 0.25 }}
              >
                {/* Preview */}
                <div className="project-preview">
                  <div className="project-preview-placeholder">
                    <div className="project-preview-icon">{project.previewEmoji}</div>
                    <span>Demo Preview</span>
                  </div>
                  <span className={`project-status ${project.status}`}>
                    {project.status === "live" ? "🟢 Live" : "🔵 Demo Available"}
                  </span>
                </div>

                {/* Info */}
                <div className="project-info">
                  <h3 className="project-title">{project.title}</h3>
                  <p className="project-description">{project.description}</p>

                  <ul style={{ listStyle: "none", padding: 0, margin: "0 0 16px", display: "flex", flexDirection: "column", gap: 4 }}>
                    {project.highlights.map((h) => (
                      <li key={h} style={{ fontSize: "0.82rem", color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ color: "var(--primary)", fontWeight: 700 }}>✓</span> {h}
                      </li>
                    ))}
                  </ul>

                  <div className="project-tech">
                    {project.technologies.map((t) => (
                      <span key={t}>{t}</span>
                    ))}
                  </div>

                  <div className="project-actions">
                    <a
                      href={project.github}
                      target="_blank"
                      rel="noreferrer"
                      className="project-btn github-btn"
                    >
                      <FaGithub /> GitHub
                    </a>
                    <button
                      className="project-btn demo-btn"
                      onClick={() => setDemoProject(project)}
                    >
                      <FaPlay size={10} /> Live Demo
                    </button>
                    <a href="#achievements" className="project-btn code-btn">
                      <FaCode /> See Code
                    </a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Achievements ── */}
      <section id="achievements" className="skills-section section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">Achievements</div>
            <h2 className="section-title">Key Achievements & Showcases</h2>
            <p className="section-subtitle">
              Highlighted technical accomplishments — with real code snippets and project demos.
              Want to see it running live? Request a demo below.
            </p>
          </div>

          <div className="achievements-grid">
            {achievements.map((a, i) => (
              <motion.div
                key={a.title}
                className="achievement-card fade-in-up"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {/* Media Area */}
                <div className="achievement-media">
                  <div className="media-tabs">
                    <button
                      className={`media-tab ${getAchievementTab(i) === "code" ? "active" : ""}`}
                      onClick={() => setAchievementTab((t) => ({ ...t, [i]: "code" }))}
                    >
                      Code
                    </button>
                    <button
                      className={`media-tab ${getAchievementTab(i) === "demo" ? "active" : ""}`}
                      onClick={() => setAchievementTab((t) => ({ ...t, [i]: "demo" }))}
                    >
                      Demo
                    </button>
                  </div>

                  <AnimatePresence mode="wait">
                    {getAchievementTab(i) === "code" ? (
                      <motion.div
                        key="code"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{ width: "100%", padding: "50px 16px 16px", alignSelf: "flex-end" }}
                      >
                        <CodeDisplay code={a.codeSnippet} />
                      </motion.div>
                    ) : (
                      <motion.div
                        key="demo"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="media-placeholder"
                      >
                        <div className="icon">🎬</div>
                        <span>Demo GIF</span>
                        <span style={{ fontSize: "0.7rem", marginTop: 4 }}>
                          Add your screen recording here
                        </span>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Body */}
                <div className="achievement-body">
                  <span className={`achievement-badge ${a.badge}`}>
                    {a.badge === "featured" ? "⭐ Featured" : "✅ Completed"}
                  </span>
                  <h3 className="achievement-title">{a.title}</h3>
                  <p className="achievement-desc">{a.description}</p>

                  <div className="achievement-tech">
                    {a.technologies.map((t) => (
                      <span key={t}>{t}</span>
                    ))}
                  </div>

                  <div className="achievement-actions">
                    <a
                      href={a.githubUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="project-btn github-btn"
                    >
                      <FaGithub /> View Code
                    </a>
                    <button
                      className="project-btn demo-btn"
                      onClick={() => setDemoProject({ title: a.title })}
                    >
                      <FaExternalLinkAlt size={11} /> Request Demo
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Experience ── */}
      <section id="experience" className="section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">Experience</div>
            <h2 className="section-title">Professional Journey</h2>
            <p className="section-subtitle">
              My path through backend development, AI engineering, and software architecture.
            </p>
          </div>

          <div className="experience-timeline">
            {experience.map((exp, i) => (
              <motion.div
                key={exp.role}
                className="timeline-item fade-in-up"
                style={{ animationDelay: `${i * 0.15}s` }}
              >
                <div className={`timeline-dot ${exp.current ? "current" : ""}`} />
                <div className="timeline-content">
                  <span className="timeline-date">{exp.date}</span>
                  <h3 className="timeline-role">{exp.role}</h3>
                  <p className="timeline-company">{exp.company}</p>
                  <ul className="timeline-tasks">
                    {exp.tasks.map((task) => (
                      <li key={task}>{task}</li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Contact ── */}
      <section id="contact" className="skills-section section-padding">
        <div className="section-wrapper">
          <div className="section-header fade-in-up">
            <div className="section-badge">Contact</div>
            <h2 className="section-title">Let's Work Together</h2>
            <p className="section-subtitle">
              Open to Backend Developer, AI Engineer, and Full-Stack opportunities. Let's talk.
            </p>
          </div>

          <div className="contact-grid">
            <div className="contact-info fade-in-up">
              <p>
                Whether you have a project in mind, want to collaborate on an AI experiment,
                or just want to say hi — my inbox is always open. I respond within 24 hours.
              </p>

              {[
                {
                  icon: <FaEnvelope />,
                  iconClass: "email-icon",
                  title: "Email",
                  value: "mufeed_alali@outlook.com",
                  href: "mailto:mufeed_alali@outlook.com",
                },
                {
                  icon: <FaGithub />,
                  iconClass: "github-icon",
                  title: "GitHub",
                  value: "github.com/mufeedalali",
                  href: "https://github.com/mufeedalali",
                },
                {
                  icon: <FaLinkedin />,
                  iconClass: "linkedin-icon",
                  title: "LinkedIn",
                  value: "linkedin.com/in/mufeedalali",
                  href: "https://linkedin.com/in/mufeedalali",
                },
              ].map((m) => (
                <a key={m.title} href={m.href} target="_blank" rel="noreferrer" className="contact-method">
                  <div className={`contact-icon ${m.iconClass}`}>{m.icon}</div>
                  <div className="contact-method-info">
                    <h4>{m.title}</h4>
                    <span>{m.value}</span>
                  </div>
                </a>
              ))}
            </div>

            <div className="contact-form fade-in-up stagger-2">
              <h3>Send a Message</h3>
              {formSent ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  style={{
                    textAlign: "center",
                    padding: "40px 20px",
                    color: "var(--primary)",
                  }}
                >
                  <div style={{ fontSize: "3rem", marginBottom: 12 }}>✅</div>
                  <p style={{ fontWeight: 600, color: "var(--text)" }}>Opening your email client…</p>
                  <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                    Thank you! I'll get back to you soon.
                  </p>
                </motion.div>
              ) : (
                <form onSubmit={handleFormSubmit}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                    <div className="form-group">
                      <label>Name</label>
                      <input
                        required
                        placeholder="Your name"
                        value={formState.name}
                        onChange={(e) => setFormState((s) => ({ ...s, name: e.target.value }))}
                      />
                    </div>
                    <div className="form-group">
                      <label>Email</label>
                      <input
                        type="email"
                        required
                        placeholder="Your email"
                        value={formState.email}
                        onChange={(e) => setFormState((s) => ({ ...s, email: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Subject</label>
                    <input
                      placeholder="What's this about?"
                      value={formState.subject}
                      onChange={(e) => setFormState((s) => ({ ...s, subject: e.target.value }))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Message</label>
                    <textarea
                      required
                      placeholder="Tell me about your project or opportunity…"
                      value={formState.message}
                      onChange={(e) => setFormState((s) => ({ ...s, message: e.target.value }))}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary form-submit">
                    <Send size={16} /> Send Message
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-logo">Mufeed Alali</div>

          <nav className="footer-links">
            {navLinks.map((l) => (
              <a key={l.href} href={l.href}>{l.label}</a>
            ))}
          </nav>

          <div className="footer-social">
            <a href="https://github.com/mufeedalali" target="_blank" rel="noreferrer" aria-label="GitHub">
              <FaGithub />
            </a>
            <a href="https://linkedin.com/in/mufeedalali" target="_blank" rel="noreferrer" aria-label="LinkedIn">
              <FaLinkedin />
            </a>
            <a href="mailto:mufeed_alali@outlook.com" aria-label="Email">
              <FaEnvelope />
            </a>
          </div>

          <div className="footer-divider" />

          <p className="footer-bottom">
            © {new Date().getFullYear()} Mufeed Alali — Backend Developer & AI Engineer. Built with React & TypeScript.
          </p>
        </div>
      </footer>

      {/* ── Demo Modal ── */}
      <AnimatePresence>
        {demoProject && (
          <DemoModal project={demoProject} onClose={() => setDemoProject(null)} />
        )}
      </AnimatePresence>
    </>
  );
}

export default App;
