const reduceMotionQuery = matchMedia('(prefers-reduced-motion: reduce)');
const revealTargets = document.querySelectorAll('[data-reveal]');

const revealAll = () => {
  revealTargets.forEach((node) => node.classList.add('is-visible'));
};

if (reduceMotionQuery.matches || !('IntersectionObserver' in window)) {
  revealAll();
} else {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.2,
      rootMargin: '0px 0px -8% 0px',
    }
  );

  revealTargets.forEach((node) => observer.observe(node));
}
