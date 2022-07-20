import {useEffect, useState} from "react";

export const useUserList = () => {
  const [userResponseData, setUserResponseData] = useState<any[]>([]);
  const [postResponseData, setPostResponseData] = useState<any[]>([]);

  // Get all user data and post data in the hook as it's a fairly small list and will only require two queries.
  // Filtering posts in the query by userId is possible but is simpler to do in the component itself
  // so that we don't need to refetch any data
  useEffect(() => {
    const fetchUserData = async () => {
      await fetch(
          "https://jsonplaceholder.typicode.com/users"
      )
          .then(data => data.json())
          .then((data) => {
            setUserResponseData(data);
          })
    };
    if(userResponseData.length  === 0){
        fetchUserData();
    }

    const fetchPostData = async () => {
      await fetch(
          "https://jsonplaceholder.typicode.com/posts"
      )
          .then(data => data.json())
          .then((data) => {
            setPostResponseData(data);
          })
    };
    if(postResponseData.length === 0){
        fetchPostData();
    }
  }, []);

  const userData = userResponseData?.map((user) => {
      // for each user find all posts belonging to the user and find the latest
      // (by using ID as a proxy for creation date)
      const userPosts = postResponseData?.filter((post) => {
          return post.userId === user.id
      })
      const latestPost = userPosts?.sort((a, b) => {
          return b.id - a.id
      })[0]
      return {
          id: user?.id,
          name: user?.name,
          lastPostTitle: latestPost?.title,
          lastPostBody: latestPost?.body,
      };
  });

  return { userData }
};