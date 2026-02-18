import { performance } from 'perf_hooks';

// Generate a large dataset
const generateFAQs = (count) => {
  const items = [];
  const categories = ['setup', 'voice', 'phone', 'billing', 'troubleshooting'];
  for (let i = 0; i < count; i++) {
    items.push({
      category: categories[i % categories.length],
      question: `Question ${i} about something important`,
      answer: `Answer ${i} with some detailed text to search through.`,
      popular: i % 10 === 0
    });
  }
  return items;
};

const faqItems = generateFAQs(10000); // 10k items to make it measurable
const searchQuery = 'detailed';
const selectedCategory = 'voice';

// Unoptimized: Filter every time
const runUnoptimized = (iterations) => {
  const start = performance.now();
  for (let i = 0; i < iterations; i++) {
    const filteredFAQ = faqItems.filter(item => {
      const matchesSearch = item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.answer.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }
  return performance.now() - start;
};

// Optimized: Memoized (simulated)
// In a real React app, useMemo would skip the calculation if deps don't change.
// So we simulate "re-renders" where deps DON'T change.
const runOptimized = (iterations) => {
  const start = performance.now();
  let filteredFAQ;
  let lastSearchQuery = null;
  let lastSelectedCategory = null;

  for (let i = 0; i < iterations; i++) {
    // Check dependencies
    if (searchQuery !== lastSearchQuery || selectedCategory !== lastSelectedCategory) {
       filteredFAQ = faqItems.filter(item => {
        const matchesSearch = item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             item.answer.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
        return matchesSearch && matchesCategory;
      });
      lastSearchQuery = searchQuery;
      lastSelectedCategory = selectedCategory;
    }
    // Else: reuse filteredFAQ
  }
  return performance.now() - start;
};

const iterations = 1000;
console.log(`Benchmarking with ${faqItems.length} items and ${iterations} iterations...`);

const unoptimizedTime = runUnoptimized(iterations);
console.log(`Unoptimized time: ${unoptimizedTime.toFixed(2)}ms`);

const optimizedTime = runOptimized(iterations);
console.log(`Optimized time: ${optimizedTime.toFixed(2)}ms`);

if (optimizedTime > 0) {
  console.log(`Improvement: ${(unoptimizedTime / optimizedTime).toFixed(2)}x faster`);
} else {
  console.log('Optimized time was too fast to measure accurately.');
}
