import { FaGithub, FaLinkedin, FaEnvelope } from "react-icons/fa";
import { Download, Mail } from "lucide-react";
import { motion } from "framer-motion";

const skills = [
  "Node.js",
  "TypeScript",
  "React",
  "Next.js",
  "Python",
  "PHP",
  "Symfony",
  "PostgreSQL",
  "MongoDB",
  "Docker",
  "AWS",
  "GitHub Actions",
  "RabbitMQ",
  "LangChain",
  "OpenAI API",
  "RAG",
  "Vector Databases",
];

const projects = [
  {
    title: "AI Document Assistant",
    description:
      "A Retrieval-Augmented Generation application allowing users to search and interact with documents using Large Language Models.",
    technologies:
      "Python • LangChain • OpenAI API • ChromaDB • FastAPI • React",
    github: "#",
  },
  {
    title: "AI Coding Assistant",
    description:
      "An AI assistant helping developers understand, analyze and improve source code using LLM capabilities.",
    technologies: "Node.js • TypeScript • OpenAI API • React",
    github: "#",
  },
  {
    title: "Scalable Backend Platform",
    description:
      "Backend services with REST APIs, authentication, database optimization and automated deployment pipelines.",
    technologies:
      "Node.js • PostgreSQL • Docker • RabbitMQ • CI/CD • GitHub Actions",
    github: "#",
  },
];

function App() {
  return (
    <div className="container">
      <section className="hero">
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          Mufeed Alali
        </motion.h1>

        <h2>Backend Developer | Node.js | AI Engineer</h2>

        <p>
          I build scalable backend systems and AI-powered applications using
          modern technologies.
        </p>

        <div className="buttons">
          <a href="/cv.pdf">
            <Download size={18} />
            CV
          </a>

          <a href="https://github.com/mufeedalali">
            <FaGithub size={18} />
            GitHub
          </a>

          <a href="https://linkedin.com">
            <FaLinkedin size={18} />
            LinkedIn
          </a>
        </div>
      </section>

      <section>
        <h2>About Me</h2>

        <p>
          Software developer specialized in backend and full-stack development.
          Experienced in building APIs, distributed systems, database-driven
          applications and integrating Artificial Intelligence capabilities with
          modern LLM technologies.
        </p>
      </section>

      <section>
        <h2>Technical Skills</h2>

        <div className="skills">
          {skills.map((skill) => (
            <span key={skill}>{skill}</span>
          ))}
        </div>
      </section>

      <section>
        <h2>Projects</h2>

        {projects.map((project) => (
          <article key={project.title}>
            <h3>{project.title}</h3>

            <p>{project.description}</p>

            <strong>{project.technologies}</strong>
          </article>
        ))}
      </section>

      <section>
        <h2>Experience</h2>

        <p>
          Developed production applications, designed backend APIs, improved
          performance and reliability, worked with Docker, CI/CD pipelines,
          databases and cloud environments.
        </p>
      </section>

      <section>
        <h2>Contact</h2>

        <p>Open to Backend Developer and AI Engineer opportunities.</p>

        <a href="mailto:mufeed_alali@outlook.com">
          <Mail size={18} />
          Email me
        </a>
      </section>
    </div>
  );
}

export default App;
