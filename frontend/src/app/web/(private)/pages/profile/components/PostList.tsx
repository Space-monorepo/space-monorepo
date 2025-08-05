import PostCard from "./PostCard";

export default function PostList() {
  const posts = [
    { title: "Título 1", description: "Descrição 1", likes: 582, comments: 120, timeAgo: "45 min" },
    { title: "Título 2", description: "Descrição 2", likes: 300, comments: 80, timeAgo: "16d" },
  ];

  return (
    <div className="space-y-4">
      {posts.map((post, index) => (
        <PostCard key={index} {...post} />
      ))}
    </div>
  );
}