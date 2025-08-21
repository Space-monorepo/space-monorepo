import * as React from "react";
import SignUpForm from "./components/SignUpForm";
import SignUpLayout from "./components/SignUpLayout";

export default function SignupPage() {
  return (
    <SignUpLayout>
      <SignUpForm />
    </SignUpLayout>
  );
}
