# Task002: Managing Variables in Terraform
## Mark the correct answer as '[x]'

### Question 1: Why is using variables considered a good practice?

- [ ] a) Variables make the code run faster in the Azure cloud.
- [ ] b) Variables are required by Azure, otherwise the Resource Group will not be created.
- [x] c) They allow you to separate configuration values from the code logic, making it easier to reuse the same code across different environments.


### Question 2: Which of the following blocks correctly defines a variable for the location name in the variables.tf file?

- [ ] a) `variable { location = "westeurope" }`
- [x] b) `variable "location" { type = string; default = "westeurope" }`
- [ ] c) `variable "location" : "westeurope"`
 

### Question 3: How do you reference the defined variable named `location` inside the main.tf file?

- [ ] a) `$location`
- [ ] b) `variables.location` 
- [x] c) `var.location`


### Question 4: What happens if you define a variable without the `default` parameter and you don't pass its value in any other way?

- [x] a) When running the `plan` or `apply` command, Terraform will prompt you to manually enter the value in the terminal.
- [ ] b) Terraform will automatically generate a random name for your resource.
- [ ] c) The code won't run and will immediately throw a syntax error.