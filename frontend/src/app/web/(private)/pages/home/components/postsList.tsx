import Post from "./post";

interface PostData {
  id: string;
  title: string;
  content: string;
  upvotes: number;
  comments: number;
  // Add other fields of the Post object here
}

interface PostsListProps {
  posts: PostData[];
}

const PostsList: React.FC<PostsListProps> = ({ posts }) => {
  return (
    <div className="space-y-4">
      {posts.map(post => (
        <Post 
              location={""} tag={""} tagColor={""} views={0} imageType={null} key={post.id}
              {...post}        />
      ))}
    </div>
  );
};

export default PostsList;