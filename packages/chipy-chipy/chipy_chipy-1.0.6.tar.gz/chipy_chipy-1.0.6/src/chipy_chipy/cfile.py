def cfile(name):
  open(name, "x")
  with open(name, "a") as f:
    f.write("nice job. you created a file.")

# nice job.